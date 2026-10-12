import test from "node:test";
import assert from "node:assert/strict";
import { runInNewContext } from "node:vm";
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
  resolveUiLocale
} from "../library.js";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const appSource = readFileSync(join(root, "app.js"), "utf8");

function createAppHarness(storage = new Map(), { userAgent = "", onLine = true } = {}) {
  const makeElement = () => ({
    attributes: {},
    children: [],
    dataset: {},
    listeners: new Map(),
    style: {},
    value: "",
    textContent: "",
    className: "",
    innerHTML: "",
    addEventListener(type, callback) {
      this.listeners.set(type, callback);
    },
    append(child) {
      this.children.push(child);
    },
    querySelectorAll(selector) {
      return selector === "dd" ? this.summaryCells || [] : [];
    },
    setAttribute(name, value) {
      this.attributes[name] = value;
    },
    click() {}
  });
  const selectors = [
    "#cache-hint", "#clear-notes", "#clear-workspace-cache", "#document-badge",
    "#document-list", "#export-notes", "#workspace-file", "#install-hint",
    "#language-select", "#load-demo", "#review-notes", "#offline-hint",
    "#platform-pill", "#report-badge", "#report-preview", "#report-title",
    "#status-message", "#workspace-summary"
  ];
  const elements = new Map(selectors.map((selector) => [selector, makeElement()]));
  elements.get("#workspace-summary").summaryCells = Array.from({ length: 5 }, makeElement);
  const document = {
    body: { append() {} },
    documentElement: { lang: "" },
    createElement: makeElement,
    querySelector: (selector) => elements.get(selector) || makeElement(),
    querySelectorAll: () => []
  };
  const localStorage = {
    getItem: (key) => (storage.has(key) ? storage.get(key) : null),
    setItem: (key, value) => storage.set(key, String(value)),
    removeItem: (key) => storage.delete(key)
  };
  const window = { location: { search: "" }, addEventListener() {} };
  const navigator = { userAgent, onLine };
  const executableAppSource = appSource.replace(
    /^import \{[\s\S]*?\} from "\.\/library\.js";/m,
    "const { buildReviewMarkdown, getPlatformGuide, getDemoWorkspace, getUiText, parseWorkspaceText, resolveUiLocale } = globalThis.__library;"
  );
  assert.notEqual(executableAppSource, appSource, "app.js library import must be adapted for the DOM harness");
  runInNewContext(executableAppSource, {
    __library: { buildReviewMarkdown, getPlatformGuide, getDemoWorkspace, getUiText, parseWorkspaceText, resolveUiLocale },
    document,
    localStorage,
    navigator,
    window,
    URLSearchParams
  });
  return { elements, storage };
}

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
  assert.match(guide.offline_hint, /Workspace-JSON wird nicht gespeichert.*nach jedem Neuladen erneut importiert/i);
});

test("getPlatformGuide returns iOS-specific install guidance", () => {
  const guide = getPlatformGuide("Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 Version/17.5 Mobile/15E148 Safari/604.1");

  assert.equal(guide.label, "iPhone / iPad");
  assert.match(guide.install_hint, /Home-Bildschirm/);
  assert.match(guide.offline_hint, /Workspace-JSON wird nicht gespeichert.*nach jedem Neuladen erneut importiert/i);
});

test("getPlatformGuide can localize platform hints to English", () => {
  const guide = getPlatformGuide("Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 Chrome/125.0 Mobile Safari/537.36", "en");

  assert.equal(guide.label, "Android");
  assert.match(guide.install_hint, /home screen|install icon/i);
  assert.match(guide.offline_hint, /workspace JSON is not saved.*imported again after each reload/i);
});

test("getPlatformGuide can localize mobile hints to Japanese", () => {
  const guide = getPlatformGuide("Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 Version/17.5 Mobile/15E148 Safari/604.1", "ja");

  assert.equal(guide.label, "iPhone / iPad");
  assert.match(guide.install_hint, /ホーム画面/);
  assert.match(guide.offline_hint, /ワークスペース JSON は保存されない.*再読み込みのたびに再インポートが必要/);
});

test("offline guidance explains workspace re-import in all six locales", () => {
  const requiredMeaning = {
    de: /Workspace-JSON wird nicht gespeichert.*nach jedem Neuladen erneut importiert/i,
    en: /workspace JSON is not saved.*imported again after each reload/i,
    es: /JSON del espacio de trabajo no se guarda.*debe importarse de nuevo después de cada recarga/i,
    "zh-Hans": /工作区 JSON 不会保存.*每次重新加载后都必须重新导入/,
    ja: /ワークスペース JSON は保存されない.*再読み込みのたびに再インポートが必要/,
    ru: /JSON рабочей области не сохраняется.*после каждой перезагрузки его нужно импортировать заново/i
  };

  for (const [locale, pattern] of Object.entries(requiredMeaning)) {
    const guide = getPlatformGuide("Mozilla/5.0 (Linux; Android 14; Pixel 8) Chrome/125.0", locale);
    assert.match(guide.offline_hint, pattern, `${locale} offline copy must explain that workspace JSON is not persisted`);
  }
});

test("the companion ignores legacy workspace cache and requires re-import after reload", async () => {
  const workspaceCacheKey = "notespacellm-companion:last-workspace";
  const demoWorkspace = getDemoWorkspace("de");
  const storage = new Map([[workspaceCacheKey, JSON.stringify(demoWorkspace)]]);
  const firstLoad = createAppHarness(storage, {
    userAgent: "Mozilla/5.0 (Linux; Android 14; Pixel 8) Chrome/125.0",
    onLine: false
  });

  assert.equal(firstLoad.elements.get("#status-message").textContent, getUiText("de").statusNoWorkspace);
  assert.equal(firstLoad.storage.has(workspaceCacheKey), false);
  assert.match(firstLoad.elements.get("#offline-hint").textContent, /Workspace-JSON wird nicht gespeichert/);

  const workspaceFile = {
    name: "review.json",
    text: async () => JSON.stringify(demoWorkspace)
  };
  firstLoad.elements.get("#workspace-file").listeners.get("change")({ target: { files: [workspaceFile] } });
  await new Promise((resolve) => setImmediate(resolve));

  assert.equal(firstLoad.elements.get("#report-title").textContent, demoWorkspace.report.title);
  assert.equal(firstLoad.storage.has(workspaceCacheKey), false, "the imported workspace must stay in memory only");

  const afterReload = createAppHarness(storage);
  assert.equal(afterReload.elements.get("#status-message").textContent, getUiText("de").statusNoWorkspace);
  assert.equal(afterReload.elements.get("#report-title").textContent, "");
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

test("app.js speichert komplette Workspace-Payloads nicht in localStorage", () => {
  assert.doesNotMatch(
    appSource,
    /localStorage\.setItem\(\s*WORKSPACE_CACHE_KEY/,
    "Workspace-JSON darf wegen Dokumentinhalten und Berichtstext nicht persistent in localStorage landen"
  );
});

test("normalizeWorkspacePayload übernimmt die optionale Projekt-ID", () => {
  const withId = normalizeWorkspacePayload({
    schema_version: "notespacellm-workspace-v1",
    workspace: { id: "proj-123", title: "Gleicher Titel" }
  });
  const withoutId = normalizeWorkspacePayload({
    schema_version: "notespacellm-workspace-v1",
    workspace: { title: "Gleicher Titel" }
  });

  assert.equal(withId.workspace.id, "proj-123");
  assert.equal(withoutId.workspace.id, "");
});

test("app.js speichert Review-Notizen pro Projekt-ID (Titel nur als Legacy-Fallback)", () => {
  assert.match(
    appSource,
    /\$\{STORAGE_PREFIX\}id:\$\{id\}/,
    "Notizen müssen bei vorhandener Projekt-ID unter einem ID-Schlüssel liegen"
  );
  assert.match(
    appSource,
    /payload\?\.workspace\?\.id/,
    "workspaceStorageKey muss workspace.id auswerten"
  );
});
