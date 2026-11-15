// Wächter gegen veraltete Service-Worker-Caches (Vorlage: assistassets-ai/mediplaner a0363a2, PR #8).
// Der Service Worker liefert cache-first: ändert sich eine gecachte Datei, ohne dass CACHE_NAME steigt,
// behalten installierte PWAs den alten Code. ASSET_HASH bindet die Version an den Inhalt.
// Der Service Worker selbst zählt nicht mit (ein Eintrag von sich selbst wäre zirkulär; Browser prüfen ihn ohnehin per Byte-Vergleich).
// Die Dateiliste kommt aus dem Asset-Array des Service Workers selbst (inkl. Manifest und Icons);
// eine eigene Liste hier würde still veralten. Schlägt der Test fehl:
// CACHE_NAME in sw.js erhöhen und ASSET_HASH auf den genannten Wert setzen.
import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const SW = 'sw.js';
const ARRAY = 'ASSETS';
// Asset-URL im Service Worker -> Datei relativ zu ROOT ('' = ausgelassen)
const toFile = (asset) => asset.replace(/^\.\//, '');
const TEXT = /\.(html|js|mjs|css|webmanifest|json|svg|txt|xml)$/i;

const exists = (rel) => fs.existsSync(path.join(ROOT, rel));
const read = (rel) => fs.readFileSync(path.join(ROOT, rel), 'utf-8');

describe('Service-Worker-Cache', () => {
  it('ASSET_HASH passt zum Inhalt aller gecachten Dateien', () => {
    const sw = read(SW);
    const block = sw.match(new RegExp(`const ${ARRAY}\\s*=\\s*\\[([\\s\\S]*?)\\];?`));
    assert.ok(block, `${ARRAY} fehlt in ${SW}`);
    const assets = [...new Set([...block[1].matchAll(/['"]([^'"]+)['"]/g)]
      .map((m) => toFile(m[1]))
      .filter((rel) => rel !== '' && rel !== SW))];
    assert.ok(assets.includes('index.html'), `index.html fehlt in ${ARRAY}`);
    const hash = createHash('sha256');
    for (const rel of assets) {
      assert.ok(exists(rel), `In ${ARRAY} gelistet, aber nicht vorhanden: ${rel}`);
      const content = TEXT.test(rel)
        ? Buffer.from(read(rel).replace(/\r\n/g, '\n'), 'utf-8')
        : fs.readFileSync(path.join(ROOT, rel));
      hash.update(`${rel}\0`);
      hash.update(content);
    }
    const actual = hash.digest('hex').slice(0, 12);
    const recorded = sw.match(/ASSET_HASH\s*=\s*['"]([0-9a-f]{12})['"]/);
    assert.ok(recorded, `ASSET_HASH fehlt in ${SW}`);
    assert.equal(recorded[1], actual,
      `Gecachte Dateien geändert: CACHE_NAME in ${SW} erhöhen und ASSET_HASH auf '${actual}' setzen`);
  });
});
