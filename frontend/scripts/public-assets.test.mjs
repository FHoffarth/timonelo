import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, existsSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { createHash } from 'node:crypto';
import { excludeProtectedAssets, checkPublicAssets, publicMediaPlugin } from './public-assets.mjs';

const sha = value => createHash('sha256').update(value).digest('hex');
function fixture(fn) {
  const root = mkdtempSync(join(tmpdir(), 'timonelo-containment-'));
  const source = join(root, 'frontend/public'); const dist = join(root, 'frontend/dist');
  mkdirSync(source, { recursive: true }); mkdirSync(dist, { recursive: true });
  const put = (base, path, data) => { mkdirSync(dirname(join(base, path)), { recursive: true }); writeFileSync(join(base, path), data); };
  try { fn({ root, source, dist, put }); } finally { rmSync(root, { recursive: true, force: true }); }
}
function licensed(source, put) {
  const src = '/media/ships/msc-bellissima-640.webp';
  const record = { ship: 'msc-bellissima', title: 'Synthetic test photograph', author: 'Test creator',
    source_page: 'https://commons.wikimedia.org/wiki/File:Test.jpg', source_revision: 123,
    file_timestamp: '2026-01-01T00:00:00Z', retrieved_at: '2026-11-01T00:00:00Z',
    license: 'CC-BY-4.0', license_url: 'https://creativecommons.org/licenses/by/4.0/',
    rendition_license: 'CC-BY-4.0', publication_status: 'LICENSE_DOCUMENTED',
    original_url: 'https://upload.wikimedia.org/wikipedia/commons/a/ab/Test.jpg', original_sha1: 'a'.repeat(40),
    download: { sha256: sha('private test original') }, changes: 'Resized test rendition.',
    variants: [{ src, width: 640, height: 320, bytes: 14, sha256: sha('test rendition') }] };
  put(source, src.slice(1), 'test rendition');
  const manifest = { schema: 'timonelo.licensed-ship-media.v1', ships: [record] };
  put(source, 'media/ships/manifest.json', JSON.stringify(manifest));
  return { manifest, record, src };
}

test('excludes uncleared copies while retaining source originals and unrelated build files', () => fixture(({ source, dist, put }) => {
  for (const path of ['media/msc-bellissima-hero.webp', 'media/stateroom-interior.jpg', 'decks/deck_14.png', 'data/deck14.page5.png', 'hero-cruise-mist.webp']) {
    put(source, path, path); put(dist, path, path);
  }
  put(dist, 'favicon.svg', 'site icon');
  assert.throws(() => checkPublicAssets(dist, source));
  excludeProtectedAssets(dist, source);
  assert.equal(readFileSync(join(source, 'decks/deck_14.png'), 'utf8'), 'decks/deck_14.png');
  assert.equal(existsSync(join(dist, 'media/stateroom-interior.jpg')), false);
  assert.equal(existsSync(join(dist, 'favicon.svg')), true);
  checkPublicAssets(dist, source);
}));
test('rejects unlisted new media and renamed protected source bytes', () => fixture(({ source, dist, put }) => {
  put(source, 'decks/deck_14.png', 'private artwork');
  put(dist, 'assets/renamed.png', 'private artwork');
  assert.throws(() => checkPublicAssets(dist, source), /Uncleared/);
  excludeProtectedAssets(dist, source);
  put(dist, 'media/new-photo.webp', 'unreviewed new photo');
  assert.throws(() => checkPublicAssets(dist, source), /Uncleared/);
}));
test('permits only the exact licensed rendition and detects later byte mutation', () => fixture(({ source, dist, put }) => {
  const { src } = licensed(source, put); put(dist, src.slice(1), 'test rendition');
  checkPublicAssets(dist, source); excludeProtectedAssets(dist, source);
  assert.equal(existsSync(join(dist, src.slice(1))), true);
  put(dist, src.slice(1), 'mutated rendition');
  assert.throws(() => checkPublicAssets(dist, source), /integrity/);
}));
test('rejects malformed or incomplete rights mappings rather than silently approving their images', () => fixture(({ source, dist, put }) => {
  const { manifest, record } = licensed(source, put);
  for (const edit of [
    () => { record.license_url = 'https://example.invalid/license'; },
    () => { record.license_url = 'https://creativecommons.org/licenses/by/4.0/'; record.author = ''; },
    () => { record.author = 'Test creator'; record.variants[0].src = '/media/ships/../../private.webp'; },
  ]) {
    edit(); put(source, 'media/ships/manifest.json', JSON.stringify(manifest));
    assert.throws(() => excludeProtectedAssets(dist, source), /Licensed media/);
  }
}));
test('refuses to clean the public source directory or its ancestors', () => fixture(({ root, source }) => {
  assert.throws(() => excludeProtectedAssets(source, source), /separate/);
  assert.throws(() => excludeProtectedAssets(root, source), /separate/);
}));
test('does not authorize media merely because it moved outside media/decks', () => fixture(({ source, dist, put }) => {
  put(source, 'renamed/ship.jpg', 'unapproved moved image');
  put(dist, 'renamed/ship.jpg', 'unapproved moved image');
  assert.throws(() => checkPublicAssets(dist, source), /Uncleared/);
  excludeProtectedAssets(dist, source);
  assert.equal(existsSync(join(dist, 'renamed/ship.jpg')), false);
  assert.equal(existsSync(join(source, 'renamed/ship.jpg')), true);
}));
test('recognizes renamed JPEG bytes without an image extension', () => fixture(({ source, dist, put }) => {
  const bytes = Buffer.from([0xff, 0xd8, 0xff, 0xe0, 0, 0, 0, 0]);
  put(source, 'renamed/ship.bin', bytes); put(dist, 'renamed/ship.bin', bytes);
  assert.throws(() => checkPublicAssets(dist, source), /Uncleared/);
}));
test('recognizes renamed BMP and little/big-endian TIFF or BigTIFF bytes', () => fixture(({ source, dist, put }) => {
  const headers = [[0x42,0x4d,0,0,0,0,0,0], [0x49,0x49,0x2a,0], [0x4d,0x4d,0,0x2a], [0x49,0x49,0x2b,0], [0x4d,0x4d,0,0x2b]];
  for (const [i, bytes] of headers.entries()) {
    const path = `renamed/image-${i}.bin`; put(source, path, Buffer.from(bytes)); put(dist, path, Buffer.from(bytes));
  }
  assert.throws(() => checkPublicAssets(dist, source), /Uncleared/);
  excludeProtectedAssets(dist, source);
  for (const [i] of headers.entries()) assert.equal(existsSync(join(dist, `renamed/image-${i}.bin`)), false);
}));
test('detects raw evidence copies outside the normal public tree', () => fixture(({ root, source, dist, put }) => {
  put(root, 'evidence/raw/sha256/aa/test.pdf', 'held raw bytes');
  put(dist, 'assets/renamed-source.bin', 'held raw bytes');
  assert.throws(() => checkPublicAssets(dist, source), /Uncleared/);
  excludeProtectedAssets(dist, source);
  assert.equal(existsSync(join(root, 'evidence/raw/sha256/aa/test.pdf')), true);
  assert.equal(existsSync(join(dist, 'assets/renamed-source.bin')), false);
}));
test('preview refuses protected URLs before SPA fallback and leaves ordinary app routes alone', () => fixture(({ source, dist }) => {
  const plugin = publicMediaPlugin(); let middleware;
  plugin.configResolved({ command: 'serve', root: dirname(source), publicDir: source, build: { outDir: dist } });
  plugin.configurePreviewServer({ middlewares: { use(fn) { middleware = fn; } } });
  for (const path of ['/decks/deck_14.png', '/data/deck14.page5.png', '/media/msc-bellissima-hero.jpg', '/evidence/raw/sha256/test.pdf', '/%64ecks/deck_14.png?x=1']) {
    const res = { statusCode: 200, setHeader() {}, end() {} }; let next = false;
    middleware({ url: path }, res, () => { next = true; });
    assert.equal(res.statusCode, 404, path); assert.equal(next, false);
  }
  let next = false; middleware({ url: '/ships' }, {}, () => { next = true; }); assert.equal(next, true);
}));
