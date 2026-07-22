import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

import {
  buildReviewMarkdown,
  getUiText,
  getPlatformGuide,
  getDemoWorkspace,
  getSupportedUiLocales,
  normalizeWorkspacePayload,
  parseWorkspaceText,
  resolveUiLocale,
  shareReviewFile
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

test("buildReviewMarkdown supports English exports", () => {
  const workspace = getDemoWorkspace("en");
  const markdown = buildReviewMarkdown(workspace, "Re-check section 2 tomorrow.", "en");

  assert.match(markdown, /Review notes: Demo: research notes/);
  assert.match(markdown, /Question: Which core claims carry the report most strongly\?/);
  assert.match(markdown, /Re-check section 2 tomorrow\./);
});

test("buildReviewMarkdown supports Spanish exports", () => {
  const workspace = getDemoWorkspace("es");
  const markdown = buildReviewMarkdown(workspace, "Revisar la sección 2 mañana.", "es");

  assert.match(markdown, /Notas de revisión: Demo: notas de investigación/);
  assert.match(markdown, /Pregunta: ¿Qué tesis centrales/);
  assert.match(markdown, /Revisar la sección 2 mañana\./);
});

test("shareReviewFile hands a Markdown file to the mobile share sheet", async () => {
  const calls = [];
  class FakeFile {
    constructor(parts, name, options) {
      this.parts = parts;
      this.name = name;
      this.type = options.type;
    }
  }
  const navigatorApi = {
    canShare(payload) {
      calls.push(["canShare", payload]);
      return true;
    },
    async share(payload) {
      calls.push(["share", payload]);
    }
  };

  const result = await shareReviewFile({
    filename: "projekt-review-notizen.md",
    content: "# Review\n\nLokal geprüft.",
    navigatorApi,
    FileCtor: FakeFile
  });

  assert.equal(result, "shared");
  assert.equal(calls.length, 2);
  assert.equal(calls[1][1].files[0].name, "projekt-review-notizen.md");
  assert.equal(calls[1][1].files[0].type, "text/markdown");
  assert.deepEqual(calls[1][1].files[0].parts, ["# Review\n\nLokal geprüft."]);
});

test("shareReviewFile requests the existing download fallback when file sharing is unavailable", async () => {
  let shareCalled = false;
  const result = await shareReviewFile({
    filename: "review.md",
    content: "Notizen",
    navigatorApi: {
      canShare() {
        return false;
      },
      async share() {
        shareCalled = true;
      }
    },
    FileCtor: class FakeFile {}
  });

  assert.equal(result, "download");
  assert.equal(shareCalled, false);
});

test("shareReviewFile does not download after an intentional share cancellation", async () => {
  const result = await shareReviewFile({
    filename: "review.md",
    content: "Notizen",
    navigatorApi: {
      canShare() {
        return true;
      },
      async share() {
        const error = new Error("cancelled");
        error.name = "AbortError";
        throw error;
      }
    },
    FileCtor: class FakeFile {}
  });

  assert.equal(result, "cancelled");
});

test("shareReviewFile falls back to download when the platform share call fails", async () => {
  const result = await shareReviewFile({
    filename: "review.md",
    content: "Notizen",
    navigatorApi: {
      canShare() {
        return true;
      },
      async share() {
        throw new Error("share service unavailable");
      }
    },
    FileCtor: class FakeFile {}
  });

  assert.equal(result, "download");
});

test("getDemoWorkspace localizes non-Latin demo content", () => {
  const workspace = getDemoWorkspace("zh-CN");

  assert.equal(workspace.workspace.locale, "zh-Hans");
  assert.equal(workspace.workspace.title, "演示：研究笔记");
  assert.match(workspace.report.content, /# 综合/);
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

test("resolveUiLocale supports browser-style locale tags", () => {
  assert.equal(resolveUiLocale("en-US"), "en");
  assert.equal(resolveUiLocale("de-DE"), "de");
  assert.equal(resolveUiLocale("es-MX"), "es");
  assert.equal(resolveUiLocale("zh-CN"), "zh-Hans");
  assert.equal(resolveUiLocale("zh-Hans"), "zh-Hans");
  assert.equal(resolveUiLocale("ja-JP"), "ja");
  assert.equal(resolveUiLocale("ru-RU"), "ru");
  assert.equal(resolveUiLocale("fr-FR"), "de");
});

test("getSupportedUiLocales exposes all web companion UI locales", () => {
  assert.deepEqual(getSupportedUiLocales(), ["de", "en", "es", "zh-Hans", "ja", "ru"]);
});

test("all UI locale tables expose the same keys", () => {
  const baselineKeys = Object.keys(getUiText("de")).sort();

  for (const locale of getSupportedUiLocales()) {
    assert.deepEqual(
      Object.keys(getUiText(locale)).sort(),
      baselineKeys,
      `${locale} must expose the complete UI text contract`
    );
  }
});

test("getUiText returns English copy for en locales", () => {
  const text = getUiText("en-GB");
  assert.equal(text.loadDemo, "Load demo");
  assert.equal(text.clearNotes, "Clear notes");
});

test("getUiText returns premium-language web companion copy", () => {
  assert.equal(getUiText("es").loadDemo, "Cargar demo");
  assert.equal(getUiText("zh-CN").summaryHeading, "概览");
  assert.equal(getUiText("ja").exportNotes, "レビュー用ノートをエクスポート");
  assert.equal(getUiText("ru").clearNotes, "Очистить заметки");
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

test("getPlatformGuide can localize platform hints to English", () => {
  const guide = getPlatformGuide("Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 Chrome/125.0 Mobile Safari/537.36", "en");

  assert.equal(guide.label, "Android");
  assert.match(guide.install_hint, /home screen|install icon/i);
  assert.match(guide.offline_hint, /offline start|stored locally/i);
});

test("getPlatformGuide can localize mobile hints to Japanese", () => {
  const guide = getPlatformGuide("Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 Version/17.5 Mobile/15E148 Safari/604.1", "ja");

  assert.equal(guide.label, "iPhone / iPad");
  assert.match(guide.install_hint, /ホーム画面/);
  assert.match(guide.offline_hint, /ネットワークなし/);
});

test("parseWorkspaceText surfaces English validation messages when requested", () => {
  assert.throws(
    () => parseWorkspaceText("", "en"),
    /selected file is empty/i
  );
});

test("parseWorkspaceText surfaces Russian validation messages when requested", () => {
  assert.throws(
    () => parseWorkspaceText("", "ru"),
    /файл пуст/i
  );
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

test("Bug #1 Regression: fileInput.value-Reset in finally-Block (nicht nur im try-Erfolgsfall)", () => {
  assert.match(
    appSource,
    /finally\s*\{/,
    "handleFile muss einen finally-Block haben damit fileInput.value stets zurückgesetzt wird"
  );
  assert.match(
    appSource,
    /fileInput\.value\s*=\s*["']{2}/,
    "fileInput.value = '' muss im finally-Block stehen"
  );
});

test("Bug #2 Regression: saveNotes, saveWorkspaceCache und setLocale wrappen localStorage.setItem in try/catch", () => {
  const saveNotesMatch = appSource.match(/function saveNotes[\s\S]*?^}/m);
  assert.ok(saveNotesMatch, "saveNotes-Funktion muss im Quelltext vorhanden sein");
  assert.match(
    saveNotesMatch[0],
    /try\s*\{/,
    "saveNotes muss localStorage.setItem in try/catch wrappen (QuotaExceededError)"
  );

  const saveWorkspaceCacheMatch = appSource.match(/function saveWorkspaceCache[\s\S]*?^}/m);
  assert.ok(saveWorkspaceCacheMatch, "saveWorkspaceCache-Funktion muss im Quelltext vorhanden sein");
  assert.match(
    saveWorkspaceCacheMatch[0],
    /try\s*\{/,
    "saveWorkspaceCache muss localStorage.setItem in try/catch wrappen (QuotaExceededError)"
  );

  const setLocaleMatch = appSource.match(/function setLocale[\s\S]*?^}/m);
  assert.ok(setLocaleMatch, "setLocale-Funktion muss im Quelltext vorhanden sein");
  assert.match(
    setLocaleMatch[0],
    /try\s*\{/,
    "setLocale muss localStorage.setItem in try/catch wrappen (localStorage deaktiviert in Safari Private Browsing)"
  );
});

test("Bug #3 Regression: downloadText verwendet setTimeout für URL.revokeObjectURL (iOS Safari)", () => {
  const downloadTextMatch = appSource.match(/function downloadText[\s\S]*?^}/m);
  assert.ok(downloadTextMatch, "downloadText-Funktion muss im Quelltext vorhanden sein");
  assert.match(
    downloadTextMatch[0],
    /setTimeout/,
    "downloadText muss URL.revokeObjectURL per setTimeout verzögern — synchrones Revoke bricht iOS Safari Download"
  );
  assert.ok(
    !downloadTextMatch[0].includes("URL.revokeObjectURL(url);\n"),
    "URL.revokeObjectURL darf nicht synchron nach link.click() stehen"
  );
});

test("app.js uses the share-or-download contract for review exports", () => {
  assert.match(appSource, /await shareReviewFile\(\{ filename, content: markdown \}\)/);
  assert.match(appSource, /outcome === "cancelled"/);
  assert.match(appSource, /outcome === "download"/);
  assert.match(appSource, /currentText\.notesShared\(filename\)/);
});
