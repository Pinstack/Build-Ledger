// Sync the canonical, redacted public/build-ledger.json (repo root) into the site:
//   - src/data/build-ledger.json  -> imported and rendered at build time
//   - public/build-ledger.json    -> served beside the page so a reader can diff page-vs-file (AD-8)
// The canonical file is the single source of truth; these are generated copies (gitignored).
import { mkdirSync, copyFileSync, existsSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const src = resolve(here, '../../public/build-ledger.json');
const dests = [resolve(here, '../src/data/build-ledger.json'), resolve(here, '../public/build-ledger.json')];

if (!existsSync(src)) {
  console.error(`sync-ledger: canonical ledger not found at ${src}\n` +
                `Run the collector (python3 collector/collect.py) or seed (python3 collector/seed.py) first.`);
  process.exit(1);
}
for (const d of dests) {
  mkdirSync(dirname(d), { recursive: true });
  copyFileSync(src, d);
}
console.log('sync-ledger: build-ledger.json -> src/data + public');
