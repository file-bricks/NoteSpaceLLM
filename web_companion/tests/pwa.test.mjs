// Strukturtests für web_companion — kein npm install erforderlich
import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = join(__dirname, '..');

function readText(rel) { return readFileSync(join(root, rel), 'utf8'); }
function readJson(rel) { return JSON.parse(readText(rel)); }

// ──────────────────────────────────────────────────────────────
// manifest.webmanifest
// ──────────────────────────────────────────────────────────────

describe('manifest.webmanifest', () => {
  const manifest = readJson('manifest.webmanifest');

  it('hat das Pflichtfeld id', () => {
    assert.ok('id' in manifest, 'Fehlendes Feld: id');
  });

  it('hat das Pflichtfeld scope', () => {
    assert.ok('scope' in manifest, 'Fehlendes Feld: scope');
  });

  it('hat korrekten name', () => {
    assert.equal(manifest.name, 'NoteSpaceLLM Companion');
  });

  it('hat display: standalone', () => {
    assert.equal(manifest.display, 'standalone');
  });

  it('hat start_url', () => {
    assert.ok(manifest.start_url, 'Fehlendes Feld: start_url');
  });

  it('hat mindestens 4 Icons', () => {
    assert.ok(Array.isArray(manifest.icons) && manifest.icons.length >= 4, 'Weniger als 4 Icons');
  });

  it('hat ein maskable Icon', () => {
    const hasMaskable = manifest.icons.some((i) => i.purpose === 'maskable');
    assert.ok(hasMaskable, 'Kein maskable-Icon gefunden');
  });

  it('hat 192×192 und 512×512 Icon', () => {
    const sizes = manifest.icons.map((i) => i.sizes);
    assert.ok(sizes.includes('192x192'), 'Kein 192x192 Icon');
    assert.ok(sizes.includes('512x512'), 'Kein 512x512 Icon');
  });
});

// ──────────────────────────────────────────────────────────────
// Physische Icon-Dateien
// ──────────────────────────────────────────────────────────────

describe('Icons — physische Dateien', () => {
  const iconNames = [
    'Icon-192.png',
    'Icon-512.png',
    'Icon-maskable-192.png',
    'Icon-maskable-512.png',
  ];

  for (const name of iconNames) {
    it(`icons/${name} existiert`, () => {
      assert.ok(existsSync(join(root, 'icons', name)), `Fehlende Datei: icons/${name}`);
    });
  }
});

// ──────────────────────────────────────────────────────────────
// Service Worker
// ──────────────────────────────────────────────────────────────

describe('sw.js', () => {
  const sw = readText('sw.js');

  it('CACHE_NAME enthält "notespacellm"', () => {
    assert.ok(sw.includes('notespacellm'), 'CACHE_NAME enthält nicht "notespacellm"');
  });

  it('enthält skipWaiting()', () => {
    assert.ok(sw.includes('skipWaiting'), 'skipWaiting() fehlt in sw.js');
  });

  it('enthält clients.claim()', () => {
    assert.ok(sw.includes('clients.claim'), 'clients.claim() fehlt in sw.js');
  });

  it('enthält install-Event-Listener', () => {
    assert.ok(sw.includes('"install"') || sw.includes("'install'"), 'install-Listener fehlt');
  });

  it('enthält activate-Event-Listener', () => {
    assert.ok(sw.includes('"activate"') || sw.includes("'activate'"), 'activate-Listener fehlt');
  });

  it('enthält fetch-Event-Listener', () => {
    assert.ok(sw.includes('"fetch"') || sw.includes("'fetch'"), 'fetch-Listener fehlt');
  });

  it('cached mindestens einen Icon-Pfad', () => {
    assert.ok(sw.includes('./icons/Icon-192.png'), 'Icon-Pfad fehlt in sw.js ASSETS');
  });

  // Bug #2: caches.match ohne ignoreSearch schlägt bei ?demo=1-URLs offline fehl
  it('caches.match nutzt ignoreSearch:true', () => {
    assert.ok(
      /caches\.match\([^)]*ignoreSearch\s*:\s*true/.test(sw),
      'caches.match muss { ignoreSearch: true } nutzen — sonst Offline-Fail bei ?-URLs'
    );
  });
});

// ──────────────────────────────────────────────────────────────
// HTML-Integrationskette
// ──────────────────────────────────────────────────────────────

describe('index.html — Integration', () => {
  const html = readText('index.html');

  it('verlinkt manifest.webmanifest', () => {
    assert.ok(html.includes('manifest.webmanifest'), 'manifest-Link fehlt in index.html');
  });

  it('lädt app.js als Modul', () => {
    assert.ok(html.includes('app.js'), 'app.js-Script fehlt in index.html');
  });
});

// ──────────────────────────────────────────────────────────────
// app.js importiert library.js
// ──────────────────────────────────────────────────────────────

describe('app.js', () => {
  const app = readText('app.js');

  it('importiert library.js', () => {
    assert.ok(app.includes('./library.js'), 'import von library.js fehlt in app.js');
  });
});

// ──────────────────────────────────────────────────────────────
// index.html iOS-PWA-Meta
// ──────────────────────────────────────────────────────────────

describe('index.html iOS-PWA-Meta', () => {
  const html = readText('index.html');

  it('viewport-Meta enthält width=device-width und initial-scale=1', () => {
    assert.match(html, /<meta[^>]*name="viewport"[^>]*width=device-width/);
    assert.match(html, /<meta[^>]*name="viewport"[^>]*initial-scale=1/);
  });

  it('viewport-Meta enthält viewport-fit=cover', () => {
    assert.match(html, /<meta[^>]*name="viewport"[^>]*viewport-fit=cover/);
  });

  it('apple-mobile-web-app-status-bar-style ist gesetzt', () => {
    assert.match(
      html,
      /<meta[^>]*name="apple-mobile-web-app-status-bar-style"[^>]*content="[^"]+"/
    );
  });

  it('apple-mobile-web-app-title ist gesetzt', () => {
    assert.match(
      html,
      /<meta[^>]*name="apple-mobile-web-app-title"[^>]*content="[^"]+"/
    );
  });

  it('apple-touch-icon verweist auf ./icons/apple-touch-icon-180.png', () => {
    assert.match(
      html,
      /<link[^>]*rel="apple-touch-icon"[^>]*href="\.\/icons\/apple-touch-icon-180\.png"/
    );
  });

  it('apple-touch-icon hat sizes="180x180"', () => {
    assert.match(html, /<link[^>]*rel="apple-touch-icon"[^>]*sizes="180x180"/);
  });

  it('manifest-Link ist vorhanden', () => {
    assert.match(html, /<link[^>]*rel="manifest"/);
  });

  it('theme-color Meta-Tag ist gesetzt', () => {
    assert.match(html, /<meta[^>]*name="theme-color"[^>]*content="[^"]+"/);
  });

  it('keine doppelten viewport-Meta-Tags', () => {
    const matches = html.match(/<meta[^>]*name="viewport"/g) ?? [];
    assert.equal(
      matches.length,
      1,
      `Genau 1 viewport-Meta erwartet, gefunden: ${matches.length}`
    );
  });
});

// ──────────────────────────────────────────────────────────────
// Icons — apple-touch-icon-180.png
// ──────────────────────────────────────────────────────────────

describe('Icons — apple-touch-icon-180.png', () => {
  it('icons/apple-touch-icon-180.png existiert', () => {
    assert.ok(
      existsSync(join(root, 'icons', 'apple-touch-icon-180.png')),
      'Fehlende Datei: icons/apple-touch-icon-180.png'
    );
  });
});
