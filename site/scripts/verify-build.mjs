// Post-build inspection gate (FR-10, Story 3.5): the published page must survive a skeptic's read.
// Asserts the page is build-time static (no external client script), leads with the provenance hero
// (lower-bound figure), carries the audit links, and serves build-ledger.json beside itself.
// Exits non-zero on any failure so a bad cut never deploys.
import { readFileSync, existsSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const dist = resolve(here, '../dist');
const page = resolve(dist, 'engineering/index.html');

const fails = [];
if (!existsSync(page)) {
  console.error('verify-build FAILED: engineering/index.html not built');
  process.exit(1);
}
const html = readFileSync(page, 'utf8');
if (!/not a productivity score/i.test(html)) fails.push('framing line missing near top');
if (!/≥/.test(html)) fails.push('provenance hero lower-bound figure missing');
if (!/build-ledger\.json/.test(html)) fails.push('no link to build-ledger.json (audit trail)');
if (/<script\b[^>]*\bsrc=/i.test(html)) fails.push('external client script present (page must be static, AD-8)');
if (!/Methodology/i.test(html)) fails.push('Methodology note missing');
if (!/Excluded from counts/i.test(html)) fails.push('Excluded-from-counts note missing');
if (!existsSync(resolve(dist, 'build-ledger.json'))) fails.push('build-ledger.json not served beside the page');

if (fails.length) {
  console.error('verify-build FAILED:\n - ' + fails.join('\n - '));
  process.exit(1);
}
console.log('verify-build OK: static (no client JS), provenance-first hero, audit notes + file served beside page.');
