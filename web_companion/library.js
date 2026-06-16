const DEFAULT_APP = Object.freeze({
  name: "NoteSpaceLLM",
  version: "unbekannt",
  exported_at: ""
});

const SUPPORTED_UI_LOCALES = Object.freeze(["de", "en"]);

const UI_TEXT = Object.freeze({
  de: Object.freeze({
    pageTitle: "NoteSpaceLLM Web/PWA Companion",
    pageDescription: "Lokaler Web/PWA-Companion für exportierte NoteSpaceLLM-Workspaces: mobile Review-Notizen, Berichtsvorschau und Dokumentmetadaten ohne Server-Upload.",
    ogTitle: "NoteSpaceLLM Web/PWA Companion",
    ogDescription: "Read-only Browser-Companion für exportierte NoteSpaceLLM-Workspaces mit lokalen Review-Notizen und ohne Server-Upload.",
    eyebrow: "NoteSpaceLLM Companion",
    heroTitle: "Lokaler Review-Reader für exportierte Workspaces",
    heroCopy: "Der Companion importiert notespacellm-workspace-v1.json direkt im Browser, bleibt read-only für den Workspace und exportiert nur eigene Review-Notizen.",
    heroBadgePrivacy: "Kein Upload",
    heroBadgeOffline: "Offline-fähig",
    heroBadgePlatforms: "Android / iOS / Web",
    selectWorkspace: "Workspace wählen",
    loadDemo: "Demo laden",
    languageLabel: "Sprache",
    statusNoWorkspace: "Noch kein Workspace geladen.",
    androidIosPwa: "Android/iOS-PWA",
    platformDetecting: "Plattform wird erkannt …",
    installHintPending: "Install-Hinweise werden nach dem Laden im Browser angezeigt.",
    offlineHintPending: "Offline-Status wird geprüft.",
    clearWorkspaceCache: "Workspace-Cache löschen",
    summaryHeading: "Überblick",
    summaryProject: "Projekt",
    summaryQuestion: "Frage",
    summaryDocuments: "Dokumente",
    summaryExcerpts: "Auszüge",
    summaryReport: "Bericht",
    summaryProvider: "Provider",
    reportHeading: "Bericht",
    reportBadgeEmpty: "Kein Bericht",
    reportTitleEmpty: "Noch kein Export geladen",
    reportPreviewEmpty: "Importiere einen Workspace, um Bericht und Metadaten lokal anzuzeigen.",
    documentsHeading: "Dokumente",
    documentListEmpty: "Noch keine Dokumente geladen.",
    reviewNotesHeading: "Review-Notizen",
    notesBadge: "Lokal im Browser",
    notesLabel: "Eigene Beobachtungen, offene Fragen oder mobile Review-Punkte:",
    notesPlaceholder: "Beispiel: Abschnitt 3 genauer prüfen, Quellenvergleich mit Bericht vom Vortag nötig ...",
    exportNotes: "Review-Notizen exportieren",
    clearNotes: "Notizen leeren",
    cacheHintEmpty: "Noch kein Workspace für Offline-Starts gespeichert.",
    cacheHintWithTitle: (title) => `Letzter Offline-Workspace: ${title}.`,
    offlineStateOnline: "Aktuell online; ein frischer Import kann lokal zwischengespeichert werden.",
    offlineStateOffline: "Aktuell offline; der letzte lokal gespeicherte Workspace bleibt verfügbar.",
    noLeadQuestion: "Keine Leitfrage",
    selectedDocuments: (selected, total) => `${selected} von ${total} ausgewählt`,
    excerptCount: (count) => `${count} Auszüge`,
    documentCount: (count) => `${count} Einträge`,
    reportContentEmpty: "Kein Bericht im Export enthalten.",
    noDocumentsInExport: "Der Export enthält keine Dokumente.",
    noExcerptsInExport: "Keine Auszüge im Export.",
    excerptFallback: "Auszug",
    selectedPill: "Ausgewählt",
    notSelectedPill: "Nicht ausgewählt",
    unknownFormat: "unbekannt",
    noPathHint: "ohne Pfadhinweis",
    contentIncluded: "Inhalt enthalten",
    metadataOnly: "nur Metadaten",
    workspaceLoaded: (sourceLabel, title) => `${sourceLabel} geladen: ${title}`,
    loadWorkspaceFirst: "Zuerst einen Workspace laden.",
    notesExported: (filename) => `Review-Notizen exportiert: ${filename}`,
    notesCleared: "Lokale Review-Notizen geleert.",
    cacheCleared: "Lokaler Workspace-Cache gelöscht. Die aktuelle Ansicht bleibt bis zum Neuladen sichtbar.",
    reviewFilenameSuffix: "review-notizen",
    workspaceLoadErrorEmpty: "Die ausgewählte Datei ist leer.",
    workspaceLoadErrorJson: "Die Datei ist kein gültiges JSON.",
    workspaceLoadErrorObject: "Der Workspace muss ein JSON-Objekt sein.",
    workspaceLoadErrorSchema: (schemaVersion) => `Nicht unterstützte Schema-Version: ${schemaVersion}`,
    untitledWorkspace: "Unbenannter Workspace",
    untitledDocument: (index) => `Dokument ${index + 1}`,
    reportDefaultTitle: "Bericht",
    providerUnknown: "unbekannt",
    modeUnknown: "unbekannt",
    reviewHeadingWithTitle: (title) => `# Review-Notizen: ${title}`,
    reviewExportedAt: "Exportiert",
    reviewQuestion: "Leitfrage",
    reviewReport: "Bericht",
    reviewDocuments: "Dokumente",
    reviewExcerpts: "Auszüge",
    reviewNotesSection: "## Notizen",
    reviewNotesEmpty: "_Keine zusätzlichen Review-Notizen._",
    sourceLabelDemo: "Demo-Workspace",
    sourceLabelCached: "Lokaler Offline-Workspace",
    platformAndroidLabel: "Android",
    platformAndroidInstallHint: "In Chrome über das Menü oder das Installieren-Symbol zum Startbildschirm hinzufügen.",
    platformAndroidOfflineHint: "Nach dem ersten Import bleibt der zuletzt geladene Workspace lokal für einen späteren Offline-Start verfügbar.",
    platformIosLabel: "iPhone / iPad",
    platformIosInstallHint: "In Safari über Teilen → Zum Home-Bildschirm die PWA sichern.",
    platformIosOfflineHint: "Nach dem ersten Import kann der zuletzt geladene Workspace auch ohne Netz erneut geöffnet werden.",
    platformBrowserLabel: "Browser",
    platformBrowserInstallHint: "Der Companion läuft im Browser; auf Android oder iOS kann er zusätzlich als PWA gespeichert werden.",
    platformBrowserOfflineHint: "Für einen Offline-Start muss mindestens einmal ein Workspace lokal importiert worden sein."
  }),
  en: Object.freeze({
    pageTitle: "NoteSpaceLLM Web/PWA Companion",
    pageDescription: "Local Web/PWA companion for exported NoteSpaceLLM workspaces: mobile review notes, report preview, and document metadata without any server upload.",
    ogTitle: "NoteSpaceLLM Web/PWA Companion",
    ogDescription: "Read-only browser companion for exported NoteSpaceLLM workspaces with local review notes and no server upload.",
    eyebrow: "NoteSpaceLLM Companion",
    heroTitle: "Local review reader for exported workspaces",
    heroCopy: "The companion imports notespacellm-workspace-v1.json directly in the browser, stays read-only for the workspace, and exports only your own review notes.",
    heroBadgePrivacy: "No upload",
    heroBadgeOffline: "Offline-ready",
    heroBadgePlatforms: "Android / iOS / Web",
    selectWorkspace: "Choose workspace",
    loadDemo: "Load demo",
    languageLabel: "Language",
    statusNoWorkspace: "No workspace loaded yet.",
    androidIosPwa: "Android/iOS PWA",
    platformDetecting: "Detecting platform …",
    installHintPending: "Install guidance appears after the page loads in the browser.",
    offlineHintPending: "Checking offline status.",
    clearWorkspaceCache: "Clear workspace cache",
    summaryHeading: "Overview",
    summaryProject: "Project",
    summaryQuestion: "Question",
    summaryDocuments: "Documents",
    summaryExcerpts: "Excerpts",
    summaryReport: "Report",
    summaryProvider: "Provider",
    reportHeading: "Report",
    reportBadgeEmpty: "No report",
    reportTitleEmpty: "No export loaded yet",
    reportPreviewEmpty: "Import a workspace to show the report and metadata locally.",
    documentsHeading: "Documents",
    documentListEmpty: "No documents loaded yet.",
    reviewNotesHeading: "Review notes",
    notesBadge: "Stored locally",
    notesLabel: "Your own observations, open questions, or mobile review points:",
    notesPlaceholder: "Example: review section 3 more closely, compare sources with yesterday's report ...",
    exportNotes: "Export review notes",
    clearNotes: "Clear notes",
    cacheHintEmpty: "No workspace stored for offline starts yet.",
    cacheHintWithTitle: (title) => `Last offline workspace: ${title}.`,
    offlineStateOnline: "Currently online; a fresh import can be cached locally.",
    offlineStateOffline: "Currently offline; the last locally saved workspace remains available.",
    noLeadQuestion: "No guiding question",
    selectedDocuments: (selected, total) => `${selected} of ${total} selected`,
    excerptCount: (count) => `${count} excerpts`,
    documentCount: (count) => `${count} items`,
    reportContentEmpty: "No report included in the export.",
    noDocumentsInExport: "The export contains no documents.",
    noExcerptsInExport: "No excerpts included in the export.",
    excerptFallback: "Excerpt",
    selectedPill: "Selected",
    notSelectedPill: "Not selected",
    unknownFormat: "unknown",
    noPathHint: "no path hint",
    contentIncluded: "content included",
    metadataOnly: "metadata only",
    workspaceLoaded: (sourceLabel, title) => `${sourceLabel} loaded: ${title}`,
    loadWorkspaceFirst: "Load a workspace first.",
    notesExported: (filename) => `Review notes exported: ${filename}`,
    notesCleared: "Local review notes cleared.",
    cacheCleared: "Local workspace cache cleared. The current view remains visible until reloading.",
    reviewFilenameSuffix: "review-notes",
    workspaceLoadErrorEmpty: "The selected file is empty.",
    workspaceLoadErrorJson: "The file is not valid JSON.",
    workspaceLoadErrorObject: "The workspace must be a JSON object.",
    workspaceLoadErrorSchema: (schemaVersion) => `Unsupported schema version: ${schemaVersion}`,
    untitledWorkspace: "Untitled workspace",
    untitledDocument: (index) => `Document ${index + 1}`,
    reportDefaultTitle: "Report",
    providerUnknown: "unknown",
    modeUnknown: "unknown",
    reviewHeadingWithTitle: (title) => `# Review notes: ${title}`,
    reviewExportedAt: "Exported",
    reviewQuestion: "Question",
    reviewReport: "Report",
    reviewDocuments: "Documents",
    reviewExcerpts: "Excerpts",
    reviewNotesSection: "## Notes",
    reviewNotesEmpty: "_No additional review notes._",
    sourceLabelDemo: "Demo workspace",
    sourceLabelCached: "Local offline workspace",
    platformAndroidLabel: "Android",
    platformAndroidInstallHint: "In Chrome, use the menu or install icon to add the app to your home screen.",
    platformAndroidOfflineHint: "After the first import, the last loaded workspace remains stored locally for a later offline start.",
    platformIosLabel: "iPhone / iPad",
    platformIosInstallHint: "In Safari, use Share → Add to Home Screen to save the PWA.",
    platformIosOfflineHint: "After the first import, the last loaded workspace can be opened again even without a network connection.",
    platformBrowserLabel: "Browser",
    platformBrowserInstallHint: "The companion runs in the browser; on Android or iOS it can also be saved as a PWA.",
    platformBrowserOfflineHint: "For an offline start, at least one workspace must have been imported locally."
  })
});

const DEFAULT_WORKSPACE = Object.freeze({
  title: "Unbenannter Workspace",
  question: "",
  workflow_type: "",
  locale: "de"
});

function asString(value, fallback = "") {
  return typeof value === "string" ? value : fallback;
}

function asBoolean(value, fallback = false) {
  return typeof value === "boolean" ? value : fallback;
}

function asArray(value) {
  return Array.isArray(value) ? value : [];
}

function normalizeUiLocaleCandidate(value) {
  const candidate = asString(value).trim().toLowerCase();
  if (!candidate) {
    return "";
  }
  if (candidate.startsWith("en")) {
    return "en";
  }
  if (candidate.startsWith("de")) {
    return "de";
  }
  return "";
}

export function resolveUiLocale(...candidates) {
  for (const candidate of candidates) {
    const locale = normalizeUiLocaleCandidate(candidate);
    if (locale) {
      return locale;
    }
  }
  return "de";
}

export function getSupportedUiLocales() {
  return [...SUPPORTED_UI_LOCALES];
}

export function getUiText(locale = "de") {
  return UI_TEXT[resolveUiLocale(locale)];
}

function toDocumentId(index) {
  return `doc-${index + 1}`;
}

function normalizeExcerpt(excerpt, index) {
  return {
    id: asString(excerpt?.id, `excerpt-${index + 1}`),
    text: asString(excerpt?.text),
    source_hint: asString(excerpt?.source_hint)
  };
}

function normalizeDocument(document, index, uiText) {
  const excerpts = asArray(document?.excerpts)
    .map(normalizeExcerpt)
    .filter((entry) => entry.text);

  return {
    id: asString(document?.id, toDocumentId(index)),
    name: asString(document?.name, uiText.untitledDocument(index)),
    path_hint: asString(document?.path_hint),
    format: asString(document?.format),
    selected: asBoolean(document?.selected, false),
    content_included: asBoolean(document?.content_included, false),
    excerpts
  };
}

export function parseWorkspaceText(text, locale = "de") {
  const uiText = getUiText(locale);
  if (!asString(text).trim()) {
    throw new Error(uiText.workspaceLoadErrorEmpty);
  }

  let raw;
  try {
    raw = JSON.parse(text);
  } catch {
    throw new Error(uiText.workspaceLoadErrorJson);
  }

  return normalizeWorkspacePayload(raw, locale);
}

export function normalizeWorkspacePayload(payload, locale = "de") {
  const uiText = getUiText(locale);
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
    throw new Error(uiText.workspaceLoadErrorObject);
  }

  const schemaVersion = asString(payload.schema_version);
  if (schemaVersion && schemaVersion !== "notespacellm-workspace-v1") {
    throw new Error(uiText.workspaceLoadErrorSchema(schemaVersion));
  }

  const documents = asArray(payload.documents).map((document, index) =>
    normalizeDocument(document, index, uiText)
  );
  const excerpts = documents.flatMap((document) => document.excerpts);
  const selectedDocuments = documents.filter((document) => document.selected);
  const reportContent = asString(payload.report?.content);
  const chatMessages = asArray(payload.chat?.messages);

  return {
    schema_version: schemaVersion || "notespacellm-workspace-v1",
    app: {
      ...DEFAULT_APP,
      name: asString(payload.app?.name, DEFAULT_APP.name),
      version: asString(payload.app?.version, DEFAULT_APP.version),
      exported_at: asString(payload.app?.exported_at, DEFAULT_APP.exported_at)
    },
    workspace: {
      ...DEFAULT_WORKSPACE,
      title: asString(payload.workspace?.title, uiText.untitledWorkspace),
      question: asString(payload.workspace?.question, DEFAULT_WORKSPACE.question),
      workflow_type: asString(payload.workspace?.workflow_type, DEFAULT_WORKSPACE.workflow_type),
      locale: asString(payload.workspace?.locale, DEFAULT_WORKSPACE.locale)
    },
    documents,
    report: {
      title: asString(payload.report?.title, uiText.reportDefaultTitle),
      format: asString(payload.report?.format, reportContent ? "markdown" : uiText.reportBadgeEmpty),
      content: reportContent
    },
    chat: {
      messages: chatMessages
    },
    provider: {
      mode: asString(payload.provider?.mode, uiText.modeUnknown),
      name: asString(payload.provider?.name, uiText.providerUnknown),
      secret_exported: asBoolean(payload.provider?.secret_exported, false)
    },
    summary: {
      document_count: documents.length,
      selected_count: selectedDocuments.length,
      excerpt_count: excerpts.length,
      chat_message_count: chatMessages.length,
      has_report: Boolean(reportContent.trim())
    }
  };
}

export function buildReviewMarkdown(workspacePayload, notes, locale = "") {
  const uiText = getUiText(locale || workspacePayload?.workspace?.locale || "de");
  const title = asString(workspacePayload?.workspace?.title, uiText.untitledWorkspace);
  const question = asString(workspacePayload?.workspace?.question, uiText.noLeadQuestion);
  const reportTitle = asString(workspacePayload?.report?.title, uiText.reportDefaultTitle);
  const exportedAt = asString(workspacePayload?.app?.exported_at, uiText.providerUnknown);
  const excerptCount = workspacePayload?.summary?.excerpt_count ?? 0;
  const documentCount = workspacePayload?.summary?.document_count ?? 0;
  const reportFormat = asString(workspacePayload?.report?.format, uiText.providerUnknown);
  const noteBody = asString(notes).trim() || uiText.reviewNotesEmpty;

  return [
    uiText.reviewHeadingWithTitle(title),
    "",
    `- ${uiText.reviewExportedAt}: ${exportedAt}`,
    `- ${uiText.reviewQuestion}: ${question}`,
    `- ${uiText.reviewReport}: ${reportTitle} (${reportFormat})`,
    `- ${uiText.reviewDocuments}: ${documentCount}`,
    `- ${uiText.reviewExcerpts}: ${excerptCount}`,
    "",
    uiText.reviewNotesSection,
    "",
    noteBody
  ].join("\n");
}

export function getPlatformGuide(userAgent = "", locale = "de") {
  const agent = asString(userAgent).toLowerCase();
  const uiText = getUiText(locale);

  if (agent.includes("android")) {
    return {
      label: uiText.platformAndroidLabel,
      install_hint: uiText.platformAndroidInstallHint,
      offline_hint: uiText.platformAndroidOfflineHint
    };
  }

  if (/(iphone|ipad|ipod)/.test(agent)) {
    return {
      label: uiText.platformIosLabel,
      install_hint: uiText.platformIosInstallHint,
      offline_hint: uiText.platformIosOfflineHint
    };
  }

  return {
    label: uiText.platformBrowserLabel,
    install_hint: uiText.platformBrowserInstallHint,
    offline_hint: uiText.platformBrowserOfflineHint
  };
}

export function getDemoWorkspace(locale = "de") {
  const resolvedLocale = resolveUiLocale(locale);
  const demoPayload = resolvedLocale === "en"
    ? {
        schema_version: "notespacellm-workspace-v1",
        app: {
          name: "NoteSpaceLLM",
          version: "1.0.0",
          exported_at: "2026-05-28T10:00:00Z"
        },
        workspace: {
          title: "Demo: research notes",
          question: "Which core claims carry the report most strongly?",
          workflow_type: "research",
          locale: "en"
        },
        documents: [
          {
            id: "doc-1",
            name: "report-draft.md",
            path_hint: "reports/report-draft.md",
            format: "markdown",
            selected: true,
            content_included: false,
            excerpts: [
              {
                id: "doc-1-excerpt-1",
                text: "The strongest evidence comes from combining the primary source with an explicit cross-check.",
                source_hint: "Section 2"
              }
            ]
          },
          {
            id: "doc-2",
            name: "literature.pdf",
            path_hint: "sources/literature.pdf",
            format: "pdf",
            selected: true,
            content_included: false,
            excerpts: [
              {
                id: "doc-2-excerpt-1",
                text: "Several studies point to the same methodological bottleneck.",
                source_hint: "Page 14"
              }
            ]
          }
        ],
        report: {
          title: "Synthesis report",
          format: "markdown",
          content: "# Synthesis\n\n- Core claim A is supported by two sources.\n- Open gap: comparative data for 2024 is still missing."
        },
        chat: {
          messages: [
            {
              role: "assistant",
              content: "Summarize the evidence base for the main claim."
            }
          ]
        },
        provider: {
          mode: "local",
          name: "ollama",
          secret_exported: false
        }
      }
    : {
        schema_version: "notespacellm-workspace-v1",
        app: {
          name: "NoteSpaceLLM",
          version: "1.0.0",
          exported_at: "2026-05-28T10:00:00Z"
        },
        workspace: {
          title: "Demo: Forschungsnotizen",
          question: "Welche Kernthesen tragen den Bericht am stärksten?",
          workflow_type: "research",
          locale: "de"
        },
        documents: [
          {
            id: "doc-1",
            name: "berichtsentwurf.md",
            path_hint: "berichte/berichtsentwurf.md",
            format: "markdown",
            selected: true,
            content_included: false,
            excerpts: [
              {
                id: "doc-1-excerpt-1",
                text: "Die stärkste Evidenz liegt in der Kombination aus Primärquelle und Gegenprüfung.",
                source_hint: "Abschnitt 2"
              }
            ]
          },
          {
            id: "doc-2",
            name: "literatur.pdf",
            path_hint: "quellen/literatur.pdf",
            format: "pdf",
            selected: true,
            content_included: false,
            excerpts: [
              {
                id: "doc-2-excerpt-1",
                text: "Mehrere Studien weisen auf denselben methodischen Engpass hin.",
                source_hint: "Seite 14"
              }
            ]
          }
        ],
        report: {
          title: "Synthesebericht",
          format: "markdown",
          content: "# Synthese\n\n- Kernthese A wird durch zwei Quellen gestützt.\n- Offene Lücke: Vergleichsdaten für 2024 fehlen noch."
        },
        chat: {
          messages: [
            {
              role: "assistant",
              content: "Fasse die Quellenlage für die Hauptthese zusammen."
            }
          ]
        },
        provider: {
          mode: "local",
          name: "ollama",
          secret_exported: false
        }
      };

  return normalizeWorkspacePayload(demoPayload, resolvedLocale);
}
