#!/usr/bin/env node
import { access } from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath, pathToFileURL } from 'node:url';

const MAX_INPUT_CHARS = 2_500_000;
const bridgeDir = path.dirname(fileURLToPath(import.meta.url));
const projectRoot = path.resolve(bridgeDir, '..');

async function readRequest() {
  process.stdin.setEncoding('utf8');
  let input = '';
  for await (const chunk of process.stdin) {
    input += chunk;
    if (input.length > MAX_INPUT_CHARS) {
      throw new Error('bridge input exceeds the 2.5 MB limit');
    }
  }
  const value = JSON.parse(input);
  if (value === null || typeof value !== 'object' || Array.isArray(value)) {
    throw new TypeError('bridge request must be a JSON object');
  }
  return value;
}

async function loadConverter() {
  const configuredRoot = process.env.HTML_TO_ARKUI_ROOT;
  const packageRoot = configuredRoot
    ? path.resolve(configuredRoot)
    : path.join(projectRoot, 'node_modules', '@local', 'html-to-arkui');
  const entry = path.join(packageRoot, 'dist', 'index.js');
  try {
    await access(entry);
  } catch {
    const hint = configuredRoot
      ? `build html-to-arkui at ${packageRoot}`
      : 'run npm ci --ignore-scripts --offline in the UIBench repository';
    throw new Error(`html-to-arkui runtime not found at ${entry}; ${hint}`);
  }
  return import(pathToFileURL(entry).href);
}

function publicAssetFiles(files) {
  return (files ?? []).map((file) => ({
    sourcePath: file.sourcePath,
    logicalName: file.logicalName,
    mimeType: file.mimeType,
    byteLength: file.content?.byteLength ?? 0,
  }));
}

async function execute(request) {
  const converter = await loadConverter();
  if (request.action === 'render-screen-ir') {
    const validation = converter.validateScreenIr(request.screenIr);
    if (!validation.valid) {
      return {
        ok: false,
        error: {
          code: 'SCREEN_IR_INVALID',
          message: 'Screen IR validation failed',
          details: validation,
        },
      };
    }
    return {
      ok: true,
      result: {
        screenIr: request.screenIr,
        arkTs: converter.renderScreenIrToArkTs(request.screenIr),
        validation,
      },
    };
  }
  if (request.action === 'convert-html') {
    const options = request.options ?? {};
    const result = converter.convertHtmlToArkUi(request.html, options);
    return {
      ok: true,
      result: {
        ...result,
        assetFiles: publicAssetFiles(result.assetFiles),
      },
    };
  }
  if (request.action === 'contract') {
    return {
      ok: true,
      result: {
        screenIrSchemaVersion: converter.SCREEN_IR_SCHEMA_VERSION,
        components: converter.getArkUiComponentDefinitions(),
      },
    };
  }
  throw new TypeError(`unsupported bridge action: ${String(request.action)}`);
}

try {
  const response = await execute(await readRequest());
  process.stdout.write(JSON.stringify(response));
  if (!response.ok) process.exitCode = 2;
} catch (error) {
  process.stdout.write(JSON.stringify({
    ok: false,
    error: {
      code: 'ARKUI_BRIDGE_FAILED',
      message: error instanceof Error ? error.message : String(error),
    },
  }));
  process.exitCode = 1;
}
