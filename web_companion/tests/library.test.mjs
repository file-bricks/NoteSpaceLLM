import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

import {
  buildReviewMarkdown,
  getPlatformGuide,
  getDemoWorkspace,
  normalizeWorkspacePayload,
  parseWorkspaceText
} from "../library.js";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const appSource = readFileSync(join(root, "app.js"), "utf8");

test("normalizeWorkspacePayload accepts minimal valid payload", () => {
  const payload = normalizeWorkspacePayload({
    schema_version: "notespacellm-workspace-v1",
    workspace: {
      title: "Review-Projekt"
    },
    documents: [
      {
        name: "quelle.pdf",
        excerpts: [{ text: "Wichtiger Auszug." }]
      }
    ]
  });

  assert.equal(payload.workspace.title, "Review-Projekt");
  assert.equal(payload.summary.document_count, 1);
  assert.equal(payload.summary.excerpt_count, 1);
  assert.equal(payload.documents[0].id, "doc-1");
});

test("parseWorkspaceText rejects unsupported schema versions", () => {
  assert.throws(
    () => parseWorkspaceText(JSON.stringify({ schema_version: "notespacellm-workspace-v2" })),
    /Nicht unterstützte Schema-Version/
  );
});

test("buildReviewMarkdown includes workspace metadata and notes", () => {
  const workspace = getDemoWorkspace();
  const markdown = buildReviewMarkdown(workspace, "Zwei Quellen morgen gegenlesen.");

  assert.match(markdown, /Review-Notizen: Demo: Forschungsnotizen/);
  assert.match(markdown, /Leitfrage: Welche Kernthesen tragen den Bericht am stärksten\?/);
  assert.match(markdown, /Zwei Quellen morgen gegenlesen\./);
});

test("normalizeWorkspacePayload ignores malformed documents container", () => {
  const payload = normalizeWorkspacePayload({
    schema_version: "notespacellm-workspace-v1",
    documents: {
      name: "falsch"
    }
  });

  assert.equal(payload.summary.document_count, 0);
  assert.deepEqual(payload.documents, []);
});

test("getPlatformGuide returns Android-specific install guidance", () => {
  const guide = getPlatformGuide("Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 Chrome/125.0 Mobile Safari/537.36");

  assert.equal(guide.label, "Android");
  assert.match(guide.install_hint, /Startbildschirm hinzufügen|Installieren/);
  assert.match(guide.offline_hint, /Offline-Start|lokal/i);
});

test("getPlatformGuide returns iOS-specific install guidance", () => {
  const guide = getPlatformGuide("Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 Version/17.5 Mobile/15E148 Safari/604.1");

  assert.equal(guide.label, "iPhone / iPad");
  assert.match(guide.install_hint, /Home-Bildschirm/);
  assert.match(guide.offline_hint, /ohne Netz|erneut geöffnet/i);
});

// Hinweis: Bug #1 + Bug #3 sind DOM-Bugs in app.js (renderDocuments).
// Node.js-Harness hat kein DOM — Quelltext-Assertions sichern die Fixes statisch.

test("app.js renderDocuments: forEach-Parameter schattet nicht DOM document (Bug #1)", () => {
  // Vor dem Fix: forEach((document) => { ... document.createElement(...)
  // Nach dem Fix: forEach((doc) => { ... document.createElement(...)
  assert.ok(
    !appSource.includes("forEach((document)"),
    "renderDocuments darf keinen Parameter namens 'document' haben — schattet DOM document und crasht"
  );
  assert.match(
    appSource,
    /forEach\(\(doc\)/,
    "renderDocuments muss Parameter 'doc' (nicht 'document') nutzen"
  );
});

test("app.js enthält escHtml-Funktion für innerHTML-Schutz (Bug #3)", () => {
  assert.match(appSource, /function escHtml/, "escHtml-Funktion muss in app.js vorhanden sein");
  assert.match(appSource, /escHtml\(doc\.name\)/, "doc.name muss über escHtml eingesetzt werden");
  assert.match(appSource, /escHtml\(excerpt\.text\)/, "excerpt.text muss über escHtml eingesetzt werden");
  assert.match(appSource, /escHtml\(excerpt\.source_hint\)/, "excerpt.source_hint muss über escHtml eingesetzt werden");
});
