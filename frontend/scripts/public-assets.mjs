import { createHash } from 'node:crypto';
import { existsSync, lstatSync, readFileSync, readdirSync, unlinkSync, openSync, readSync, closeSync } from 'node:fs';
import { dirname, join, resolve, relative, posix } from 'node:path';
import { fileURLToPath } from 'node:url';

const frontend = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const DEFAULT_SOURCE = join(frontend, 'public');
const DEFAULT_DIST = join(frontend, 'dist');
const raster = /\.(?:png|jpe?g|webp|gif|avif|bmp|tiff?)$/i;
export const PROTECTED_PATHS = [
  ...[5, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18].map(n => `decks/deck_${n}.png`),
  'data/deck14.page5.png', 'hero-cruise-mist.jpg', 'hero-cruise-mist.webp',
  'hero-cruise-golden-hour.webp', 'social-preview.jpg',
];
const licenses = {
  'CC0-1.0': 'https://creativecommons.org/publicdomain/zero/1.0/',
  'CC-BY-4.0': 'https://creativecommons.org/licenses/by/4.0/',
  'CC-BY-SA-4.0': 'https://creativecommons.org/licenses/by-sa/4.0/',
};
const hash = file => createHash('sha256').update(readFileSync(file)).digest('hex');
function imageFile(file) {
  if (raster.test(file)) return true;
  const header = Buffer.alloc(32); const fd = openSync(file, 'r');
  try { readSync(fd, header, 0, header.length, 0); } finally { closeSync(fd); }
  return header.subarray(0, 3).equals(Buffer.from([0xff, 0xd8, 0xff])) ||
    header.toString('ascii', 0, 2) === 'BM' ||
    (header.toString('ascii', 0, 2) === 'II' && [42, 43].includes(header[2]) && header[3] === 0) ||
    (header.toString('ascii', 0, 2) === 'MM' && header[2] === 0 && [42, 43].includes(header[3])) ||
    header.subarray(0, 8).equals(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10])) ||
    /^GIF8[79]a/.test(header.toString('ascii', 0, 6)) ||
    (header.toString('ascii', 0, 4) === 'RIFF' && header.toString('ascii', 8, 12) === 'WEBP') ||
    (header.toString('ascii', 4, 8) === 'ftyp' && /avif|avis/.test(header.toString('ascii', 8, 32)));
}
const text = value => typeof value === 'string' && value.trim().length > 0;
const hex = (value, size) => typeof value === 'string' && new RegExp(`^[0-9a-f]{${size}}$`).test(value);
const inside = (parent, child) => { const p = relative(resolve(parent), resolve(child)); return p === '' || (!p.startsWith('..') && !p.startsWith('/') && !/^[A-Za-z]:/.test(p)); };

function walk(root) {
  if (!existsSync(root)) return [];
  if (lstatSync(root).isSymbolicLink()) throw new Error(`Unreviewed asset symlink: ${root}`);
  return readdirSync(root).flatMap(name => {
    const path = join(root, name); const stat = lstatSync(path);
    if (stat.isSymbolicLink()) throw new Error(`Unreviewed asset symlink: ${path}`);
    return stat.isDirectory() ? walk(path) : [path];
  });
}
function licensedMedia(source) {
  const file = join(source, 'media/ships/manifest.json'); const allowed = new Map();
  if (!existsSync(file)) return allowed; // no manifest = no licensed image allowance
  if (lstatSync(file).isSymbolicLink()) throw new Error('Licensed media manifest may not be a symlink');
  const manifest = JSON.parse(readFileSync(file, 'utf8'));
  const refuse = () => { throw new Error('Licensed media mapping incomplete or inconsistent'); };
  if (manifest.schema !== 'timonelo.licensed-ship-media.v1' || !Array.isArray(manifest.ships)) refuse();
  const seen = new Set();
  for (const m of manifest.ships) {
    if (!m || !/^msc-[a-z-]+$/.test(m.ship) || seen.has(m.ship) || !text(m.author) || !text(m.title) ||
        m.publication_status !== 'LICENSE_DOCUMENTED' || !licenses[m.license] || m.license_url !== licenses[m.license] ||
        m.rendition_license !== m.license || !text(m.changes) ||
        !/^https:\/\/commons\.wikimedia\.org\/wiki\/File:[^?#]+$/.test(m.source_page) ||
        !Number.isInteger(m.source_revision) || m.source_revision < 1 ||
        !Number.isFinite(Date.parse(m.file_timestamp)) || !Number.isFinite(Date.parse(m.retrieved_at)) ||
        !/^https:\/\/upload\.wikimedia\.org\/wikipedia\/commons\//.test(m.original_url) ||
        !hex(m.original_sha1, 40) || !hex(m.download?.sha256, 64) || !Array.isArray(m.variants) || !m.variants.length) refuse();
    seen.add(m.ship);
    for (const v of m.variants) {
      if (!v || !new RegExp(`^/media/ships/${m.ship}-[1-9][0-9]*\\.webp$`).test(v.src) ||
          !hex(v.sha256, 64) || !Number.isInteger(v.width) || v.width < 1 ||
          !Number.isInteger(v.height) || v.height < 1 || !Number.isInteger(v.bytes) || v.bytes < 1 || allowed.has(v.src.slice(1))) refuse();
      const path = join(source, v.src.slice(1));
      if (!existsSync(path) || lstatSync(path).isSymbolicLink() || hash(path) !== v.sha256 || lstatSync(path).size !== v.bytes) refuse();
      allowed.set(v.src.slice(1), v.sha256);
    }
  }
  return allowed;
}
function policy(source) {
  const allowed = licensedMedia(source);
  const forbidden = new Set(PROTECTED_PATHS);
  for (const path of walk(source)) {
    const name = relative(source, path).replaceAll('\\', '/');
    if (imageFile(path) && !allowed.has(name)) forbidden.add(name);
  }
  // Every unlicensed deck raster is excluded, including future filenames.
  for (const path of walk(join(source, 'decks'))) if (raster.test(path)) forbidden.add(relative(source, path).replaceAll('\\', '/'));
  const raw = walk(resolve(source, '../../evidence/raw/sha256'));
  const sourceFiles = [...forbidden].map(p => join(source, p)).filter(existsSync);
  return { allowed, forbidden, hashes: new Set([...sourceFiles, ...raw].map(hash)) };
}
function validateOutput(dist, source) {
  if (inside(source, dist) || inside(dist, source)) throw new Error('Build output must be separate from the source tree');
  if (!existsSync(dist)) throw new Error('Production build output missing');
  if (lstatSync(dist).isSymbolicLink()) throw new Error('Build output may not be a symlink');
}
function classify(path, dist, rules) {
  const name = relative(dist, path).replaceAll('\\', '/');
  if (rules.allowed.has(name)) {
    if (hash(path) !== rules.allowed.get(name)) throw new Error(`Licensed rendition integrity failure: ${name}`);
    return false;
  }
  return rules.forbidden.has(name) ||
    imageFile(path) ||
    (name.startsWith('media/') && raster.test(name)) ||
    (name.startsWith('decks/') && raster.test(name)) ||
    name.includes('evidence/raw/sha256/') || rules.hashes.has(hash(path));
}
export function excludeProtectedAssets(dist = DEFAULT_DIST, source = DEFAULT_SOURCE) {
  validateOutput(dist, source); const rules = policy(source);
  // Walk only the validated output. Never mutate evidence, public originals or history.
  for (const path of walk(dist)) if (classify(path, dist, rules)) unlinkSync(path);
}
export function checkPublicAssets(dist = DEFAULT_DIST, source = DEFAULT_SOURCE) {
  validateOutput(dist, source); const rules = policy(source);
  for (const path of walk(dist)) if (classify(path, dist, rules)) throw new Error(`Uncleared source/media in public build: ${path}`);
}
export function publicMediaPlugin() {
  let building = false; let source = DEFAULT_SOURCE; let dist = DEFAULT_DIST;
  let runtimeRules;
  const middleware = (req, res, next) => {
    let path;
    try { path = posix.normalize(decodeURIComponent(new URL(req.url || '/', 'http://localhost').pathname)).toLowerCase(); }
    catch { res.statusCode = 400; res.end(); return; }
    if (path === '/data/fleet.publication.json') res.setHeader('Cache-Control', 'no-store, max-age=0');
    const rules = runtimeRules; const name = path.slice(1);
    const protectedURL = rules.forbidden.has(name) || (path.startsWith('/media/') && raster.test(path) && !rules.allowed.has(name)) ||
      (path.startsWith('/decks/') && raster.test(path)) || path.includes('/evidence/raw/sha256/');
    if (protectedURL) { res.statusCode = 404; res.setHeader('Cache-Control', 'no-store'); res.end('Asset withheld pending redistribution clearance'); return; }
    next();
  };
  return { name: 'public-asset-containment',
    configResolved(config) { building = config.command === 'build'; source = config.publicDir || DEFAULT_SOURCE; dist = resolve(config.root, config.build.outDir); },
    configureServer(server) { runtimeRules = policy(source); server.middlewares.use(middleware); },
    configurePreviewServer(server) { runtimeRules = policy(source); server.middlewares.use(middleware); },
    // Applies to direct vite build as well as npm run build.
    closeBundle() { if (building) { excludeProtectedAssets(dist, source); checkPublicAssets(dist, source); } },
  };
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  checkPublicAssets(); console.log('Public asset containment guard: PASS');
}
