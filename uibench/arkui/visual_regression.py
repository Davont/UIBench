"""Dependency-free PNG comparison for ArkUI visual regression artifacts.

The capture environments are deliberately kept outside this module: browsers,
DevEco Previewer, emulators, and physical devices all have different lifecycle
requirements.  This module owns the stable, deterministic part of the
contract: decoding screenshots, calculating comparable metrics, and producing
an inspectable diff PNG.
"""
from __future__ import annotations

import math
import struct
import zlib
from dataclasses import dataclass
from pathlib import Path

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
_CHANNELS_BY_COLOR_TYPE = {0: 1, 2: 3, 4: 2, 6: 4}
MAX_SCREENSHOT_PIXELS = 20_000_000
MAX_SCREENSHOT_PNG_BYTES = 64 * 1024 * 1024
MAX_PNG_CHUNKS = 4096
MAX_IDAT_BYTES = 64 * 1024 * 1024
MAX_NORMALIZED_EDGE = 3840
MAX_NORMALIZED_PIXELS = MAX_NORMALIZED_EDGE * MAX_NORMALIZED_EDGE
MAX_AREA_RESAMPLE_CONTRIBUTIONS = 25_000_000


@dataclass
class VisualRegressionError(ValueError):
    code: str
    message: str

    def __str__(self) -> str:
        return self.message


@dataclass(frozen=True)
class DecodedPng:
    width: int
    height: int
    rgba: bytes


@dataclass(frozen=True)
class VisualDiffMetrics:
    width: int
    height: int
    pixel_threshold: int
    total_pixels: int
    different_pixels: int
    different_ratio: float
    mean_absolute_error: float
    root_mean_square_error: float
    max_channel_delta: int
    different_bounding_box: tuple[int, int, int, int] | None

    def to_dict(self) -> dict[str, int | float | list[int] | None]:
        return {
            "width": self.width,
            "height": self.height,
            "pixelThreshold": self.pixel_threshold,
            "totalPixels": self.total_pixels,
            "differentPixels": self.different_pixels,
            "differentRatio": self.different_ratio,
            "meanAbsoluteError": self.mean_absolute_error,
            "rootMeanSquareError": self.root_mean_square_error,
            "maxChannelDelta": self.max_channel_delta,
            "differentBoundingBox": (
                None
                if self.different_bounding_box is None
                else list(self.different_bounding_box)
            ),
        }


@dataclass(frozen=True)
class VisualDiffResult:
    metrics: VisualDiffMetrics
    diff_png: bytes


@dataclass(frozen=True)
class PixelCrop:
    x: int
    y: int
    width: int
    height: int


@dataclass(frozen=True)
class PngNormalizationSpec:
    crop: PixelCrop
    pixels_per_content_pixel: int | None
    content_width: int
    content_height: int
    resample: str

    def to_dict(self) -> dict[str, object]:
        crop = {
            "x": self.crop.x,
            "y": self.crop.y,
            "width": self.crop.width,
            "height": self.crop.height,
        }
        viewport = {
            "width": self.content_width,
            "height": self.content_height,
        }
        if self.resample == "area-v1":
            return {
                "normalizationVersion": 2,
                "source": {"cropPx": crop},
                "target": {"contentViewport": viewport},
                "resample": self.resample,
            }
        return {
            "normalizationVersion": 1,
            "cropPx": crop,
            "scale": {
                "pixelsPerContentPixel": self.pixels_per_content_pixel,
            },
            "contentViewport": viewport,
            "resample": self.resample,
        }


def _paeth(left: int, up: int, upper_left: int) -> int:
    estimate = left + up - upper_left
    left_distance = abs(estimate - left)
    up_distance = abs(estimate - up)
    upper_left_distance = abs(estimate - upper_left)
    if left_distance <= up_distance and left_distance <= upper_left_distance:
        return left
    if up_distance <= upper_left_distance:
        return up
    return upper_left


def _png_chunks(data: bytes) -> list[tuple[bytes, bytes]]:
    if len(data) > MAX_SCREENSHOT_PNG_BYTES:
        raise VisualRegressionError(
            "UIBENCH_VISUAL_PNG_TOO_LARGE",
            "PNG file exceeds the bounded screenshot byte size",
        )
    if not data.startswith(PNG_SIGNATURE):
        raise VisualRegressionError(
            "UIBENCH_VISUAL_PNG_SIGNATURE_INVALID",
            "Screenshot is not a PNG file",
        )
    chunks: list[tuple[bytes, bytes]] = []
    offset = len(PNG_SIGNATURE)
    idat_bytes = 0
    while offset < len(data):
        if len(data) - offset < 12:
            raise VisualRegressionError(
                "UIBENCH_VISUAL_PNG_TRUNCATED",
                "PNG chunk header is truncated",
            )
        length = struct.unpack(">I", data[offset:offset + 4])[0]
        chunk_type = data[offset + 4:offset + 8]
        payload_start = offset + 8
        payload_end = payload_start + length
        crc_end = payload_end + 4
        if crc_end > len(data):
            raise VisualRegressionError(
                "UIBENCH_VISUAL_PNG_TRUNCATED",
                "PNG chunk payload is truncated",
            )
        payload = data[payload_start:payload_end]
        expected_crc = struct.unpack(">I", data[payload_end:crc_end])[0]
        actual_crc = zlib.crc32(chunk_type + payload) & 0xFFFFFFFF
        if actual_crc != expected_crc:
            raise VisualRegressionError(
                "UIBENCH_VISUAL_PNG_CRC_INVALID",
                f"PNG chunk {chunk_type.decode('ascii', 'replace')} has an invalid CRC",
            )
        if len(chunks) >= MAX_PNG_CHUNKS:
            raise VisualRegressionError(
                "UIBENCH_VISUAL_PNG_CHUNKS_EXCEEDED",
                "PNG contains too many chunks",
            )
        if chunk_type == b"tRNS":
            raise VisualRegressionError(
                "UIBENCH_VISUAL_PNG_TRANSPARENCY_UNSUPPORTED",
                "Palette or color-key PNG transparency is not supported; use RGBA",
            )
        if chunk_type == b"IDAT":
            idat_bytes += len(payload)
            if idat_bytes > MAX_IDAT_BYTES:
                raise VisualRegressionError(
                    "UIBENCH_VISUAL_PNG_IDAT_TOO_LARGE",
                    "PNG compressed image data exceeds the screenshot limit",
                )
        chunks.append((chunk_type, payload))
        offset = crc_end
        if chunk_type == b"IEND":
            if offset != len(data):
                raise VisualRegressionError(
                    "UIBENCH_VISUAL_PNG_TRAILING_DATA",
                    "PNG contains data after IEND",
                )
            return chunks
    raise VisualRegressionError(
        "UIBENCH_VISUAL_PNG_IEND_MISSING",
        "PNG does not contain an IEND chunk",
    )


def decode_png(data: bytes) -> DecodedPng:
    """Decode bounded 8-bit, non-interlaced RGB/RGBA/grayscale PNG bytes."""
    chunks = _png_chunks(data)
    ihdr_payloads = [payload for kind, payload in chunks if kind == b"IHDR"]
    if len(ihdr_payloads) != 1 or len(ihdr_payloads[0]) != 13:
        raise VisualRegressionError(
            "UIBENCH_VISUAL_PNG_IHDR_INVALID",
            "PNG must contain exactly one valid IHDR chunk",
        )
    width, height, bit_depth, color_type, compression, filtering, interlace = (
        struct.unpack(">IIBBBBB", ihdr_payloads[0])
    )
    if (
        width < 1
        or height < 1
        or width > 10_000
        or height > 10_000
        or width * height > MAX_SCREENSHOT_PIXELS
    ):
        raise VisualRegressionError(
            "UIBENCH_VISUAL_PNG_DIMENSIONS_INVALID",
            "PNG dimensions exceed the bounded screenshot area",
        )
    channels = _CHANNELS_BY_COLOR_TYPE.get(color_type)
    if (
        bit_depth != 8
        or channels is None
        or compression != 0
        or filtering != 0
        or interlace != 0
    ):
        raise VisualRegressionError(
            "UIBENCH_VISUAL_PNG_FORMAT_UNSUPPORTED",
            "Only non-interlaced 8-bit RGB, RGBA, grayscale, and grayscale-alpha PNG screenshots are supported",
        )
    compressed = b"".join(payload for kind, payload in chunks if kind == b"IDAT")
    if not compressed:
        raise VisualRegressionError(
            "UIBENCH_VISUAL_PNG_IDAT_MISSING",
            "PNG does not contain image data",
        )
    stride = width * channels
    expected_length = (stride + 1) * height
    try:
        decompressor = zlib.decompressobj()
        filtered = decompressor.decompress(compressed, expected_length + 1)
    except zlib.error as exc:
        raise VisualRegressionError(
            "UIBENCH_VISUAL_PNG_IDAT_INVALID",
            "PNG image data could not be decompressed",
        ) from exc
    if (
        len(filtered) != expected_length
        or not decompressor.eof
        or bool(decompressor.unconsumed_tail)
    ):
        raise VisualRegressionError(
            "UIBENCH_VISUAL_PNG_SCANLINES_INVALID",
            "PNG scanline length does not match its dimensions",
        )

    unfiltered = bytearray(stride * height)
    source_offset = 0
    for row_index in range(height):
        filter_type = filtered[source_offset]
        source_offset += 1
        row_start = row_index * stride
        previous_start = row_start - stride
        for column in range(stride):
            raw = filtered[source_offset + column]
            left = unfiltered[row_start + column - channels] if column >= channels else 0
            up = unfiltered[previous_start + column] if row_index else 0
            upper_left = (
                unfiltered[previous_start + column - channels]
                if row_index and column >= channels else 0
            )
            if filter_type == 0:
                value = raw
            elif filter_type == 1:
                value = raw + left
            elif filter_type == 2:
                value = raw + up
            elif filter_type == 3:
                value = raw + ((left + up) // 2)
            elif filter_type == 4:
                value = raw + _paeth(left, up, upper_left)
            else:
                raise VisualRegressionError(
                    "UIBENCH_VISUAL_PNG_FILTER_UNSUPPORTED",
                    f"PNG uses unsupported scanline filter {filter_type}",
                )
            unfiltered[row_start + column] = value & 0xFF
        source_offset += stride

    rgba = bytearray(width * height * 4)
    source_offset = 0
    target_offset = 0
    for _ in range(width * height):
        if color_type == 0:
            gray = unfiltered[source_offset]
            pixel = (gray, gray, gray, 255)
        elif color_type == 2:
            pixel = (*unfiltered[source_offset:source_offset + 3], 255)
        elif color_type == 4:
            gray, alpha = unfiltered[source_offset:source_offset + 2]
            pixel = (gray, gray, gray, alpha)
        else:
            pixel = tuple(unfiltered[source_offset:source_offset + 4])
        rgba[target_offset:target_offset + 4] = bytes(pixel)
        source_offset += channels
        target_offset += 4
    return DecodedPng(width=width, height=height, rgba=bytes(rgba))


def _chunk(kind: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    )


def encode_rgba_png(width: int, height: int, rgba: bytes) -> bytes:
    """Encode deterministic 8-bit RGBA PNG bytes for diff artifacts and tests."""
    if width < 1 or height < 1 or len(rgba) != width * height * 4:
        raise VisualRegressionError(
            "UIBENCH_VISUAL_RGBA_INVALID",
            "RGBA byte length does not match the requested dimensions",
        )
    scanlines = bytearray()
    stride = width * 4
    for row_index in range(height):
        scanlines.append(0)
        start = row_index * stride
        scanlines.extend(rgba[start:start + stride])
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return (
        PNG_SIGNATURE
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(bytes(scanlines), level=9))
        + _chunk(b"IEND", b"")
    )


def _normalization_integer(value: object) -> bool:
    return type(value) is int


def _area_resample_contributions(
    source_width: int,
    source_height: int,
    target_width: int,
    target_height: int,
) -> int:
    horizontal = source_width + target_width - math.gcd(source_width, target_width)
    vertical = source_height + target_height - math.gcd(source_height, target_height)
    if horizontal > MAX_AREA_RESAMPLE_CONTRIBUTIONS // vertical:
        raise VisualRegressionError(
            "UIBENCH_VISUAL_NORMALIZATION_TOO_EXPENSIVE",
            "Area resampling exceeds the bounded pixel-contribution budget",
        )
    return horizontal * vertical


def _normalize_integer_box(
    source: DecodedPng,
    spec: PngNormalizationSpec,
    scale: int,
) -> bytes:
    crop = spec.crop
    target = bytearray(spec.content_width * spec.content_height * 4)
    source_stride = source.width * 4
    denominator = scale * scale
    for target_y in range(spec.content_height):
        for target_x in range(spec.content_width):
            channel_totals = [0, 0, 0, 0]
            source_x = crop.x + target_x * scale
            source_y = crop.y + target_y * scale
            for block_y in range(scale):
                row_offset = (source_y + block_y) * source_stride
                for block_x in range(scale):
                    offset = row_offset + (source_x + block_x) * 4
                    for channel in range(4):
                        channel_totals[channel] += source.rgba[offset + channel]
            target_offset = (target_y * spec.content_width + target_x) * 4
            target[target_offset:target_offset + 4] = bytes(
                (total + denominator // 2) // denominator
                for total in channel_totals
            )
    return bytes(target)


def _normalize_area(source: DecodedPng, spec: PngNormalizationSpec) -> bytes:
    crop = spec.crop
    target_width = spec.content_width
    target_height = spec.content_height
    _area_resample_contributions(
        crop.width,
        crop.height,
        target_width,
        target_height,
    )
    target = bytearray(target_width * target_height * 4)
    source_stride = source.width * 4
    denominator = crop.width * crop.height
    doubled_denominator = denominator * 2

    # Source and target pixel cells are projected onto a shared integer grid.
    # The complete two-dimensional numerator is accumulated before the sole
    # half-up rounding step, so the result is independent of floating point.
    for target_y in range(target_height):
        target_y_start = target_y * crop.height
        target_y_end = (target_y + 1) * crop.height
        source_y_start = target_y_start // target_height
        source_y_stop = (target_y_end + target_height - 1) // target_height
        for target_x in range(target_width):
            target_x_start = target_x * crop.width
            target_x_end = (target_x + 1) * crop.width
            source_x_start = target_x_start // target_width
            source_x_stop = (target_x_end + target_width - 1) // target_width
            red = green = blue = 0
            for source_y in range(source_y_start, source_y_stop):
                source_y_cell_start = source_y * target_height
                source_y_cell_end = (source_y + 1) * target_height
                weight_y = min(source_y_cell_end, target_y_end) - max(
                    source_y_cell_start, target_y_start
                )
                row_offset = (crop.y + source_y) * source_stride
                for source_x in range(source_x_start, source_x_stop):
                    source_x_cell_start = source_x * target_width
                    source_x_cell_end = (source_x + 1) * target_width
                    weight_x = min(source_x_cell_end, target_x_end) - max(
                        source_x_cell_start, target_x_start
                    )
                    weight = weight_x * weight_y
                    offset = row_offset + (crop.x + source_x) * 4
                    red += source.rgba[offset] * weight
                    green += source.rgba[offset + 1] * weight
                    blue += source.rgba[offset + 2] * weight
            target_offset = (target_y * target_width + target_x) * 4
            target[target_offset:target_offset + 4] = bytes((
                (2 * red + denominator) // doubled_denominator,
                (2 * green + denominator) // doubled_denominator,
                (2 * blue + denominator) // doubled_denominator,
                255,
            ))
    return bytes(target)


def normalize_png_bytes(data: bytes, spec: PngNormalizationSpec) -> bytes:
    """Crop and deterministically resample an opaque device screenshot."""
    source = decode_png(data)
    crop = spec.crop
    common_integers = (
        crop.x,
        crop.y,
        crop.width,
        crop.height,
        spec.content_width,
        spec.content_height,
    )
    if (
        not all(_normalization_integer(value) for value in common_integers)
        or crop.x < 0
        or crop.y < 0
        or crop.width < 1
        or crop.height < 1
        or spec.content_width < 1
        or spec.content_height < 1
    ):
        raise VisualRegressionError(
            "UIBENCH_VISUAL_NORMALIZATION_INVALID",
            "Normalization crop and viewport must use positive bounded integers",
        )
    if (
        crop.x > source.width
        or crop.y > source.height
        or crop.width > source.width - crop.x
        or crop.height > source.height - crop.y
    ):
        raise VisualRegressionError(
            "UIBENCH_VISUAL_NORMALIZATION_CROP_OUT_OF_BOUNDS",
            "Normalization crop must stay inside the raw screenshot",
        )

    scale = spec.pixels_per_content_pixel
    if spec.resample == "area-v1":
        if scale is not None:
            raise VisualRegressionError(
                "UIBENCH_VISUAL_NORMALIZATION_RESAMPLE_INVALID",
                "area-v1 is defined only by source crop and target viewport",
            )
        if (
            spec.content_width > MAX_NORMALIZED_EDGE
            or spec.content_height > MAX_NORMALIZED_EDGE
            or spec.content_width
            > MAX_NORMALIZED_PIXELS // spec.content_height
        ):
            raise VisualRegressionError(
                "UIBENCH_VISUAL_NORMALIZATION_INVALID",
                "Area normalization target exceeds the bounded viewport size",
            )
    else:
        if (
            not _normalization_integer(scale)
            or scale < 1
            or scale > 8
        ):
            raise VisualRegressionError(
                "UIBENCH_VISUAL_NORMALIZATION_INVALID",
                "Integer normalization scale must be between 1 and 8",
            )
        if (
            crop.width != spec.content_width * scale
            or crop.height != spec.content_height * scale
        ):
            raise VisualRegressionError(
                "UIBENCH_VISUAL_NORMALIZATION_SCALE_MISMATCH",
                "Crop dimensions must equal the content viewport times integer scale",
            )
        expected_resample = "identity" if scale == 1 else "box-v1"
        if spec.resample != expected_resample:
            raise VisualRegressionError(
                "UIBENCH_VISUAL_NORMALIZATION_RESAMPLE_INVALID",
                f"Scale {scale} requires resample={expected_resample}",
            )

    if any(source.rgba[offset] != 255 for offset in range(3, len(source.rgba), 4)):
        raise VisualRegressionError(
            "UIBENCH_VISUAL_SCREENSHOT_TRANSPARENT",
            "Raw screenshots must use an opaque full-screen canvas",
        )
    target = (
        _normalize_area(source, spec)
        if spec.resample == "area-v1"
        else _normalize_integer_box(source, spec, scale)
    )
    return encode_rgba_png(spec.content_width, spec.content_height, target)


def read_png_file(path: str | Path) -> bytes:
    """Read at most one bounded screenshot without trusting its stat size."""
    screenshot = Path(path)
    with screenshot.open("rb") as handle:
        data = handle.read(MAX_SCREENSHOT_PNG_BYTES + 1)
    if len(data) > MAX_SCREENSHOT_PNG_BYTES:
        raise VisualRegressionError(
            "UIBENCH_VISUAL_PNG_TOO_LARGE",
            f"PNG file exceeds the screenshot byte limit: {screenshot}",
        )
    return data


def compare_png_bytes(
    browser_png: bytes,
    arkui_png: bytes,
    *,
    pixel_threshold: int = 0,
) -> VisualDiffResult:
    """Compare two same-size PNG screenshots and return metrics plus a diff."""
    if not 0 <= pixel_threshold <= 255:
        raise VisualRegressionError(
            "UIBENCH_VISUAL_THRESHOLD_INVALID",
            "pixel_threshold must be between 0 and 255",
        )
    browser = decode_png(browser_png)
    arkui = decode_png(arkui_png)
    if (browser.width, browser.height) != (arkui.width, arkui.height):
        raise VisualRegressionError(
            "UIBENCH_VISUAL_DIMENSIONS_MISMATCH",
            "Browser and ArkUI screenshots must have identical dimensions",
        )
    if any(
        image.rgba[offset] != 255
        for image in (browser, arkui)
        for offset in range(3, len(image.rgba), 4)
    ):
        raise VisualRegressionError(
            "UIBENCH_VISUAL_SCREENSHOT_TRANSPARENT",
            "Browser and ArkUI screenshots must use an opaque full-screen canvas",
        )

    different_pixels = 0
    channel_absolute_total = 0
    channel_square_total = 0
    max_channel_delta = 0
    minimum_x = browser.width
    minimum_y = browser.height
    maximum_x = -1
    maximum_y = -1
    diff_rgba = bytearray(len(browser.rgba))
    for offset in range(0, len(browser.rgba), 4):
        browser_pixel = browser.rgba[offset:offset + 4]
        arkui_pixel = arkui.rgba[offset:offset + 4]
        deltas = tuple(abs(left - right) for left, right in zip(
            browser_pixel, arkui_pixel, strict=True,
        ))
        pixel_delta = max(deltas)
        channel_absolute_total += sum(deltas)
        channel_square_total += sum(delta * delta for delta in deltas)
        max_channel_delta = max(max_channel_delta, pixel_delta)
        if pixel_delta > pixel_threshold:
            different_pixels += 1
            pixel_index = offset // 4
            x = pixel_index % browser.width
            y = pixel_index // browser.width
            minimum_x = min(minimum_x, x)
            minimum_y = min(minimum_y, y)
            maximum_x = max(maximum_x, x)
            maximum_y = max(maximum_y, y)
            intensity = max(48, pixel_delta)
            diff_rgba[offset:offset + 4] = bytes((255, 0, 0, intensity))
        else:
            red, green, blue, _ = browser_pixel
            gray = (red * 299 + green * 587 + blue * 114) // 1000
            muted = 224 + gray // 8
            diff_rgba[offset:offset + 4] = bytes((muted, muted, muted, 255))

    total_pixels = browser.width * browser.height
    total_channels = total_pixels * 4
    metrics = VisualDiffMetrics(
        width=browser.width,
        height=browser.height,
        pixel_threshold=pixel_threshold,
        total_pixels=total_pixels,
        different_pixels=different_pixels,
        different_ratio=round(different_pixels / total_pixels, 8),
        mean_absolute_error=round(channel_absolute_total / total_channels, 6),
        root_mean_square_error=round(
            math.sqrt(channel_square_total / total_channels), 6
        ),
        max_channel_delta=max_channel_delta,
        different_bounding_box=(
            None if different_pixels == 0 else (
                minimum_x,
                minimum_y,
                maximum_x - minimum_x + 1,
                maximum_y - minimum_y + 1,
            )
        ),
    )
    return VisualDiffResult(
        metrics=metrics,
        diff_png=encode_rgba_png(browser.width, browser.height, bytes(diff_rgba)),
    )


def compare_png_files(
    browser_path: str | Path,
    arkui_path: str | Path,
    *,
    diff_path: str | Path | None = None,
    pixel_threshold: int = 0,
) -> VisualDiffMetrics:
    """Compare screenshot files and optionally persist the deterministic diff."""
    browser_file = Path(browser_path)
    arkui_file = Path(arkui_path)
    result = compare_png_bytes(
        read_png_file(browser_file),
        read_png_file(arkui_file),
        pixel_threshold=pixel_threshold,
    )
    if diff_path is not None:
        destination = Path(diff_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(result.diff_png)
    return result.metrics


__all__ = [
    "DecodedPng",
    "MAX_IDAT_BYTES",
    "MAX_AREA_RESAMPLE_CONTRIBUTIONS",
    "MAX_NORMALIZED_EDGE",
    "MAX_NORMALIZED_PIXELS",
    "MAX_PNG_CHUNKS",
    "MAX_SCREENSHOT_PNG_BYTES",
    "MAX_SCREENSHOT_PIXELS",
    "PixelCrop",
    "PngNormalizationSpec",
    "VisualDiffMetrics",
    "VisualDiffResult",
    "VisualRegressionError",
    "compare_png_bytes",
    "compare_png_files",
    "decode_png",
    "encode_rgba_png",
    "normalize_png_bytes",
    "read_png_file",
]
