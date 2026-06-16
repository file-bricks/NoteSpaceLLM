import {
  buildReviewMarkdown,
  getPlatformGuide,
  getDemoWorkspace,
  getUiText,
  parseWorkspaceText,
  resolveUiLocale
} from "./library.js";

const STORAGE_PREFIX = "notespacellm-companion-notes:";
const WORKSPACE_CACHE_KEY = "notespacellm-companion:last-workspace";
const UI_LOCALE_KEY = "notespacellm-companion:locale";

function escHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

const elements = {
  cacheHint: document.querySelector("#cache-hint"),
  clearNotes: document.querySelector("#clear-notes"),
  clearWorkspaceCache: document.querySelector("#clear-workspace-cache"),
  documentBadge: document.querySelector("#document-badge"),
  documentList: document.querySelector("#document-list"),
  exportNotes: document.querySelector("#export-notes"),
  fileInput: document.querySelector("#workspace-file"),
  installHint: document.querySelector("#install-hint"),
  languageSelect: document.querySelector("#language-select"),
  loadDemo: document.querySelector("#load-demo"),
  notes: document.querySelector("#review-notes"),
  offlineHint: document.querySelector("#offline-hint"),
  platformPill: document.querySelector("#platform-pill"),
  reportBadge: document.querySelector("#report-badge"),
  reportPreview: document.querySelector("#report-preview"),
  reportTitle: document.querySelector("#report-title"),
  status: document.querySelector("#status-message"),
  summary: document.querySelector("#workspace-summary")
};

let currentWorkspace = null;
let currentSourceLabel = "";
let cachedWorkspaceTitle = "";
const storedLocale = globalThis.localStorage?.getItem(UI_LOCALE_KEY) || "";
let hasUserLocaleOverride = Boolean(storedLocale);
let activeLocale = resolveUiLocale(storedLocale, globalThis.navigator?.language, "de");
let currentText = getUiText(activeLocale);
let currentPlatformGuide = getPlatformGuide(globalThis.navigator?.userAgent || "", activeLocale);

function setStatus(message, isError = false) {
  elements.status.textContent = message;
  elements.status.style.color = isError ? "#b91c1c" : "";
}

function applyStaticTranslations() {
  document.documentElement.lang = activeLocale;

  document.querySelectorAll("[data-i18n]").forEach((node) => {
    const key = node.dataset.i18n;
    if (key && typeof currentText[key] === "string") {
      node.textContent = currentText[key];
    }
  });

  document.querySelectorAll("[data-i18n-placeholder]").forEach((node) => {
    const key = node.dataset.i18nPlaceholder;
    if (key && typeof currentText[key] === "string") {
      node.setAttribute("placeholder", currentText[key]);
    }
  });

  document.querySelectorAll("[data-i18n-content]").forEach((node) => {
    const key = node.dataset.i18nContent;
    if (key && typeof currentText[key] === "string") {
      node.setAttribute("content", currentText[key]);
    }
  });

  elements.languageSelect.value = activeLocale;
}

function workspaceStorageKey(payload) {
  const title = payload?.workspace?.title || "workspace";
  return `${STORAGE_PREFIX}${title}`;
}

function saveNotes() {
  if (!currentWorkspace) {
    return;
  }
  localStorage.setItem(workspaceStorageKey(currentWorkspace), elements.notes.value);
}

function updateCacheHint(title = "") {
  cachedWorkspaceTitle = title;
  elements.cacheHint.textContent = title
    ? currentText.cacheHintWithTitle(title)
    : currentText.cacheHintEmpty;
}

function updateOfflineHint() {
  const state = navigator.onLine
    ? currentText.offlineStateOnline
    : currentText.offlineStateOffline;
  elements.offlineHint.textContent = `${currentPlatformGuide.offline_hint} ${state}`;
}

function applyPlatformGuide() {
  currentPlatformGuide = getPlatformGuide(globalThis.navigator?.userAgent || "", activeLocale);
  elements.platformPill.textContent = currentPlatformGuide.label;
  elements.installHint.textContent = currentPlatformGuide.install_hint;
  updateOfflineHint();
}

function downloadText(filename, content) {
  const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.append(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function loadNotes(payload) {
  const value = localStorage.getItem(workspaceStorageKey(payload)) || "";
  elements.notes.value = value;
}

function renderSummary(payload) {
  const values = [
    payload.workspace.title,
    payload.workspace.question || currentText.noLeadQuestion,
    currentText.selectedDocuments(payload.summary.selected_count, payload.summary.document_count),
    currentText.excerptCount(payload.summary.excerpt_count),
    payload.report.title,
    `${payload.provider.name} (${payload.provider.mode})`
  ];

  [...elements.summary.querySelectorAll("dd")].forEach((node, index) => {
    node.textContent = values[index] || "-";
  });
}

function renderReport(payload) {
  elements.reportTitle.textContent = payload.report.title;
  elements.reportBadge.textContent = payload.report.format;
  elements.reportPreview.textContent = payload.report.content || currentText.reportContentEmpty;
}

function renderDocuments(payload) {
  elements.documentBadge.textContent = currentText.documentCount(payload.summary.document_count);

  if (!payload.documents.length) {
    elements.documentList.className = "stacked-list empty-state";
    elements.documentList.textContent = currentText.noDocumentsInExport;
    return;
  }

  elements.documentList.className = "stacked-list";
  elements.documentList.innerHTML = "";

  payload.documents.forEach((doc) => {
    const article = document.createElement("article");
    article.className = "doc-card";

    const excerpts = doc.excerpts.length
      ? `<div class="excerpt-list">${doc.excerpts
          .map(
            (excerpt) => `
              <div class="excerpt">
                <span class="excerpt-source">${escHtml(excerpt.source_hint) || currentText.excerptFallback}</span>
                <div>${escHtml(excerpt.text)}</div>
              </div>
            `
          )
          .join("")}</div>`
      : `<p class="doc-meta">${currentText.noExcerptsInExport}</p>`;

    article.innerHTML = `
      <div class="doc-header">
        <div class="doc-name">${escHtml(doc.name)}</div>
        <span class="pill">${doc.selected ? currentText.selectedPill : currentText.notSelectedPill}</span>
      </div>
      <div class="doc-meta">
        ${escHtml(doc.format) || currentText.unknownFormat} · ${escHtml(doc.path_hint) || currentText.noPathHint} ·
        ${doc.content_included ? currentText.contentIncluded : currentText.metadataOnly}
      </div>
      ${excerpts}
    `;

    elements.documentList.append(article);
  });
}

function saveWorkspaceCache(payload) {
  localStorage.setItem(WORKSPACE_CACHE_KEY, JSON.stringify(payload));
  updateCacheHint(payload.workspace.title);
}

function loadWorkspaceCache() {
  const raw = localStorage.getItem(WORKSPACE_CACHE_KEY);
  if (!raw) {
    updateCacheHint();
    return null;
  }

  try {
    const payload = parseWorkspaceText(raw, activeLocale);
    updateCacheHint(payload.workspace.title);
    return payload;
  } catch {
    localStorage.removeItem(WORKSPACE_CACHE_KEY);
    updateCacheHint();
    return null;
  }
}

function rerenderCurrentWorkspace() {
  if (!currentWorkspace) {
    setStatus(currentText.statusNoWorkspace);
    return;
  }

  renderSummary(currentWorkspace);
  renderReport(currentWorkspace);
  renderDocuments(currentWorkspace);
  setStatus(currentText.workspaceLoaded(currentSourceLabel, currentWorkspace.workspace.title));
}

function setLocale(locale, { persist = false } = {}) {
  activeLocale = resolveUiLocale(locale, globalThis.navigator?.language, "de");
  currentText = getUiText(activeLocale);
  applyStaticTranslations();
  updateCacheHint(cachedWorkspaceTitle);
  applyPlatformGuide();
  rerenderCurrentWorkspace();

  if (persist) {
    localStorage.setItem(UI_LOCALE_KEY, activeLocale);
    hasUserLocaleOverride = true;
  }
}

function renderWorkspace(payload, sourceLabel, options = {}) {
  const { persist = true } = options;
  if (!hasUserLocaleOverride) {
    activeLocale = resolveUiLocale(payload.workspace.locale, globalThis.navigator?.language, "de");
    currentText = getUiText(activeLocale);
    applyStaticTranslations();
  }

  currentWorkspace = payload;
  currentSourceLabel = sourceLabel;
  renderSummary(payload);
  renderReport(payload);
  renderDocuments(payload);
  loadNotes(payload);
  applyPlatformGuide();

  if (persist) {
    saveWorkspaceCache(payload);
  } else {
    updateCacheHint(payload.workspace.title);
  }

  setStatus(currentText.workspaceLoaded(sourceLabel, payload.workspace.title));
}

async function handleFile(file) {
  if (!file) {
    return;
  }

  try {
    const text = await file.text();
    const payload = parseWorkspaceText(text, activeLocale);
    renderWorkspace(payload, file.name);
    elements.fileInput.value = "";
  } catch (error) {
    setStatus(error.message, true);
  }
}

elements.fileInput.addEventListener("change", (event) => {
  const [file] = event.target.files || [];
  void handleFile(file);
});

elements.loadDemo.addEventListener("click", () => {
  renderWorkspace(getDemoWorkspace(activeLocale), currentText.sourceLabelDemo);
});

elements.exportNotes.addEventListener("click", () => {
  if (!currentWorkspace) {
    setStatus(currentText.loadWorkspaceFirst, true);
    return;
  }

  const safeTitle = currentWorkspace.workspace.title
    .replace(/[^a-z0-9-_]+/gi, "-")
    .replace(/^-+|-+$/g, "")
    .toLowerCase() || "workspace";
  const filename = `${safeTitle}-${currentText.reviewFilenameSuffix}.md`;
  const markdown = buildReviewMarkdown(currentWorkspace, elements.notes.value, activeLocale);
  downloadText(filename, markdown);
  setStatus(currentText.notesExported(filename));
});

elements.clearNotes.addEventListener("click", () => {
  elements.notes.value = "";
  saveNotes();
  setStatus(currentText.notesCleared);
});

elements.clearWorkspaceCache.addEventListener("click", () => {
  localStorage.removeItem(WORKSPACE_CACHE_KEY);
  updateCacheHint();
  setStatus(currentText.cacheCleared);
});

elements.notes.addEventListener("input", saveNotes);
elements.languageSelect.addEventListener("change", (event) => {
  setLocale(event.target.value, { persist: true });
});

const params = new URLSearchParams(window.location.search);
setLocale(activeLocale);

if (params.get("demo") === "1") {
  renderWorkspace(getDemoWorkspace(activeLocale), currentText.sourceLabelDemo);
} else {
  const cachedWorkspace = loadWorkspaceCache();
  if (cachedWorkspace) {
    renderWorkspace(cachedWorkspace, currentText.sourceLabelCached, { persist: false });
  }
}

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("./sw.js").catch(() => {
      // Offline-Support ist optional; UI bleibt auch ohne Service Worker nutzbar.
    });
  });
}

window.addEventListener("online", updateOfflineHint);
window.addEventListener("offline", updateOfflineHint);
