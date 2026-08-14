"""Build a bounded, double-clickable HTML bundle from local UI assets."""
from __future__ import annotations

import io
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit, urlunsplit


MAX_PACKAGE_ASSETS = 256
MAX_PACKAGE_ASSET_BYTES = 16_000_000
MAX_PACKAGE_TOTAL_BYTES = 64_000_000

_LOCAL_REFERENCE_RE = re.compile(
    r"(?<![A-Za-z0-9_:/.])"
    r"(?P<url>"
    r"/(?:shared\.css|design-tokens\.css|hm-fonts\.css)"
    r"|(?:/|\./)?(?:assets|gallery)/"
    r"[^\s\"'`()<>?#,;]+"
    r"(?:\?[^\s\"'`()<>#,;]*)?"
    r"(?:#[^\s\"'`()<>?,;]*)?"
    r")"
)


class HtmlPackageError(ValueError):
    """A local reference cannot be included safely in the HTML package."""

    def __init__(self, code: str, message: str, reference: str | None = None):
        super().__init__(message)
        self.code = code
        self.reference = reference


@dataclass(frozen=True)
class HtmlPackageResult:
    archive: bytes
    asset_count: int
    archive_paths: tuple[str, ...]


@dataclass(frozen=True)
class GeneratedPackageAsset:
    archive_path: str
    content: bytes


def _safe_relative_path(value: str, reference: str) -> PurePosixPath:
    decoded = unquote(value)
    path = PurePosixPath(decoded)
    if (
        not decoded
        or path.is_absolute()
        or any(part in {"", ".", ".."} for part in path.parts)
    ):
        raise HtmlPackageError(
            "UIBENCH_HTML_PACKAGE_ASSET_PATH_INVALID",
            f"本地资源路径不安全：{reference}",
            reference,
        )
    return path


def _resolved_file(root: Path, relative: PurePosixPath, reference: str) -> Path:
    resolved_root = root.resolve()
    candidate = resolved_root.joinpath(*relative.parts).resolve()
    try:
        candidate.relative_to(resolved_root)
    except ValueError as exc:
        raise HtmlPackageError(
            "UIBENCH_HTML_PACKAGE_ASSET_PATH_INVALID",
            f"本地资源越过允许目录：{reference}",
            reference,
        ) from exc
    if not candidate.is_file():
        raise HtmlPackageError(
            "UIBENCH_HTML_PACKAGE_ASSET_NOT_FOUND",
            f"HTML 引用的本地资源不存在：{reference}",
            reference,
        )
    if candidate.stat().st_size > MAX_PACKAGE_ASSET_BYTES:
        raise HtmlPackageError(
            "UIBENCH_HTML_PACKAGE_ASSET_TOO_LARGE",
            f"HTML 引用的本地资源超过 16 MB：{reference}",
            reference,
        )
    return candidate


def _archive_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    return info


def build_html_package(
    html: str,
    *,
    assets_root: Path,
    gallery_root: Path,
    generated_assets: dict[str, GeneratedPackageAsset],
    extra_files: dict[str, Path] | None = None,
) -> HtmlPackageResult:
    """Rewrite local references and package only the resources the page uses.

    ``generated_assets`` maps server-root URLs such as ``/shared.css`` to
    package members. ``extra_files`` adds files referenced by generated CSS,
    such as HarmonyOS text fonts, even though those URLs are not present in
    the HTML itself.
    """
    if not isinstance(html, str):
        raise TypeError("html must be a string")

    members: dict[str, bytes | Path] = {}
    replacements: list[tuple[int, int, str]] = []

    for match in _LOCAL_REFERENCE_RE.finditer(html):
        reference = match.group("url")
        parsed = urlsplit(reference)
        path = parsed.path
        archive_path: str
        source: bytes | Path

        generated = generated_assets.get(path)
        if generated is not None:
            archive_path = generated.archive_path
            source = generated.content
        else:
            normalized = path[2:] if path.startswith("./") else path.lstrip("/")
            if normalized.startswith("gallery/"):
                relative = _safe_relative_path(
                    normalized.removeprefix("gallery/"), reference,
                )
                archive_path = str(PurePosixPath("assets/gallery") / relative)
                source = _resolved_file(gallery_root, relative, reference)
            elif normalized.startswith("assets/"):
                relative = _safe_relative_path(
                    normalized.removeprefix("assets/"), reference,
                )
                archive_path = str(PurePosixPath("assets") / relative)
                source = _resolved_file(assets_root, relative, reference)
            else:  # The regular expression only admits the branches above.
                continue

        previous = members.get(archive_path)
        if previous is not None and previous != source:
            raise HtmlPackageError(
                "UIBENCH_HTML_PACKAGE_ASSET_COLLISION",
                f"多个本地资源会写入同一包内路径：{archive_path}",
                reference,
            )
        members[archive_path] = source
        rewritten = urlunsplit((
            "", "", archive_path, parsed.query, parsed.fragment,
        ))
        replacements.append((match.start("url"), match.end("url"), rewritten))

    for archive_path, file_path in (extra_files or {}).items():
        safe_archive_path = str(_safe_relative_path(archive_path, archive_path))
        source = _resolved_file(file_path.parent, PurePosixPath(file_path.name), archive_path)
        previous = members.get(safe_archive_path)
        if previous is not None and previous != source:
            raise HtmlPackageError(
                "UIBENCH_HTML_PACKAGE_ASSET_COLLISION",
                f"多个本地资源会写入同一包内路径：{safe_archive_path}",
                archive_path,
            )
        members[safe_archive_path] = source

    if len(members) > MAX_PACKAGE_ASSETS:
        raise HtmlPackageError(
            "UIBENCH_HTML_PACKAGE_TOO_MANY_ASSETS",
            f"HTML 包最多允许 {MAX_PACKAGE_ASSETS} 个资源",
        )

    rewritten_html = html
    for start, end, replacement in reversed(replacements):
        rewritten_html = rewritten_html[:start] + replacement + rewritten_html[end:]

    materialized: dict[str, bytes] = {}
    total_bytes = len(rewritten_html.encode("utf-8"))
    for archive_path, source in sorted(members.items()):
        content = source if isinstance(source, bytes) else source.read_bytes()
        if len(content) > MAX_PACKAGE_ASSET_BYTES:
            raise HtmlPackageError(
                "UIBENCH_HTML_PACKAGE_ASSET_TOO_LARGE",
                f"包内资源超过 16 MB：{archive_path}",
                archive_path,
            )
        total_bytes += len(content)
        if total_bytes > MAX_PACKAGE_TOTAL_BYTES:
            raise HtmlPackageError(
                "UIBENCH_HTML_PACKAGE_TOO_LARGE",
                "HTML 与本地资源合计超过 64 MB",
            )
        materialized[archive_path] = content

    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(_archive_info("index.html"), rewritten_html.encode("utf-8"))
        for archive_path, content in materialized.items():
            archive.writestr(_archive_info(archive_path), content)

    archive_paths = ("index.html", *tuple(materialized))
    return HtmlPackageResult(
        archive=output.getvalue(),
        asset_count=len(materialized),
        archive_paths=archive_paths,
    )


__all__ = [
    "GeneratedPackageAsset",
    "HtmlPackageError",
    "HtmlPackageResult",
    "build_html_package",
]
