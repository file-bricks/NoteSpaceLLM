const DEFAULT_APP = Object.freeze({
  name: "NoteSpaceLLM",
  version: "unbekannt",
  exported_at: ""
});

const SUPPORTED_UI_LOCALES = Object.freeze(["de", "en", "es", "zh-Hans", "ja", "ru"]);

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
  }),
  es: Object.freeze({
    pageTitle: "NoteSpaceLLM Web/PWA Companion",
    pageDescription: "Companion Web/PWA local para workspaces exportados de NoteSpaceLLM: notas móviles de revisión, vista previa de informes y metadatos de documentos sin subir nada al servidor.",
    ogTitle: "NoteSpaceLLM Web/PWA Companion",
    ogDescription: "Companion de navegador de solo lectura para workspaces exportados de NoteSpaceLLM, con notas locales de revisión y sin subida al servidor.",
    eyebrow: "NoteSpaceLLM Companion",
    heroTitle: "Lector local de revisión para workspaces exportados",
    heroCopy: "El companion importa notespacellm-workspace-v1.json directamente en el navegador, mantiene el workspace en solo lectura y exporta solo tus propias notas de revisión.",
    heroBadgePrivacy: "Sin subida",
    heroBadgeOffline: "Listo sin conexión",
    heroBadgePlatforms: "Android / iOS / Web",
    selectWorkspace: "Elegir workspace",
    loadDemo: "Cargar demo",
    languageLabel: "Idioma",
    statusNoWorkspace: "Aún no se ha cargado ningún workspace.",
    androidIosPwa: "PWA para Android/iOS",
    platformDetecting: "Detectando plataforma ...",
    installHintPending: "La guía de instalación aparecerá cuando la página cargue en el navegador.",
    offlineHintPending: "Comprobando estado sin conexión.",
    clearWorkspaceCache: "Borrar caché del workspace",
    summaryHeading: "Resumen",
    summaryProject: "Proyecto",
    summaryQuestion: "Pregunta",
    summaryDocuments: "Documentos",
    summaryExcerpts: "Extractos",
    summaryReport: "Informe",
    summaryProvider: "Proveedor",
    reportHeading: "Informe",
    reportBadgeEmpty: "Sin informe",
    reportTitleEmpty: "Aún no se ha cargado ningún export",
    reportPreviewEmpty: "Importa un workspace para mostrar localmente el informe y los metadatos.",
    documentsHeading: "Documentos",
    documentListEmpty: "Aún no se han cargado documentos.",
    reviewNotesHeading: "Notas de revisión",
    notesBadge: "Guardado localmente",
    notesLabel: "Observaciones propias, preguntas abiertas o puntos de revisión móvil:",
    notesPlaceholder: "Ejemplo: revisar la sección 3 con más detalle; comparar fuentes con el informe de ayer ...",
    exportNotes: "Exportar notas de revisión",
    clearNotes: "Borrar notas",
    cacheHintEmpty: "Aún no hay ningún workspace guardado para inicios sin conexión.",
    cacheHintWithTitle: (title) => `Último workspace sin conexión: ${title}.`,
    offlineStateOnline: "Actualmente en línea; una nueva importación puede guardarse localmente.",
    offlineStateOffline: "Actualmente sin conexión; el último workspace guardado localmente sigue disponible.",
    noLeadQuestion: "Sin pregunta guía",
    selectedDocuments: (selected, total) => `${selected} de ${total} seleccionados`,
    excerptCount: (count) => `${count} extractos`,
    documentCount: (count) => `${count} elementos`,
    reportContentEmpty: "El export no contiene ningún informe.",
    noDocumentsInExport: "El export no contiene documentos.",
    noExcerptsInExport: "El export no contiene extractos.",
    excerptFallback: "Extracto",
    selectedPill: "Seleccionado",
    notSelectedPill: "No seleccionado",
    unknownFormat: "desconocido",
    noPathHint: "sin pista de ruta",
    contentIncluded: "contenido incluido",
    metadataOnly: "solo metadatos",
    workspaceLoaded: (sourceLabel, title) => `${sourceLabel} cargado: ${title}`,
    loadWorkspaceFirst: "Primero carga un workspace.",
    notesExported: (filename) => `Notas de revisión exportadas: ${filename}`,
    notesCleared: "Notas de revisión locales borradas.",
    cacheCleared: "Caché local del workspace borrada. La vista actual permanece visible hasta recargar.",
    reviewFilenameSuffix: "notas-revision",
    workspaceLoadErrorEmpty: "El archivo seleccionado está vacío.",
    workspaceLoadErrorJson: "El archivo no es un JSON válido.",
    workspaceLoadErrorObject: "El workspace debe ser un objeto JSON.",
    workspaceLoadErrorSchema: (schemaVersion) => `Versión de esquema no admitida: ${schemaVersion}`,
    untitledWorkspace: "Workspace sin título",
    untitledDocument: (index) => `Documento ${index + 1}`,
    reportDefaultTitle: "Informe",
    providerUnknown: "desconocido",
    modeUnknown: "desconocido",
    reviewHeadingWithTitle: (title) => `# Notas de revisión: ${title}`,
    reviewExportedAt: "Exportado",
    reviewQuestion: "Pregunta",
    reviewReport: "Informe",
    reviewDocuments: "Documentos",
    reviewExcerpts: "Extractos",
    reviewNotesSection: "## Notas",
    reviewNotesEmpty: "_No hay notas de revisión adicionales._",
    sourceLabelDemo: "Workspace demo",
    sourceLabelCached: "Workspace local sin conexión",
    platformAndroidLabel: "Android",
    platformAndroidInstallHint: "En Chrome, usa el menú o el icono de instalación para añadir la app a la pantalla de inicio.",
    platformAndroidOfflineHint: "Tras la primera importación, el último workspace cargado queda guardado localmente para abrirlo sin conexión más tarde.",
    platformIosLabel: "iPhone / iPad",
    platformIosInstallHint: "En Safari, usa Compartir → Añadir a pantalla de inicio para guardar la PWA.",
    platformIosOfflineHint: "Tras la primera importación, el último workspace cargado puede abrirse de nuevo incluso sin red.",
    platformBrowserLabel: "Navegador",
    platformBrowserInstallHint: "El companion funciona en el navegador; en Android o iOS también puede guardarse como PWA.",
    platformBrowserOfflineHint: "Para iniciar sin conexión, primero debe importarse localmente al menos un workspace."
  }),
  "zh-Hans": Object.freeze({
    pageTitle: "NoteSpaceLLM Web/PWA Companion",
    pageDescription: "用于导出的 NoteSpaceLLM 工作区的本地 Web/PWA Companion：移动端评审笔记、报告预览和文档元数据，无需上传到服务器。",
    ogTitle: "NoteSpaceLLM Web/PWA Companion",
    ogDescription: "用于导出的 NoteSpaceLLM 工作区的只读浏览器 Companion，支持本地评审笔记且无需服务器上传。",
    eyebrow: "NoteSpaceLLM Companion",
    heroTitle: "导出工作区的本地评审阅读器",
    heroCopy: "Companion 会直接在浏览器中导入 notespacellm-workspace-v1.json，工作区保持只读，并且只导出你自己的评审笔记。",
    heroBadgePrivacy: "不上传",
    heroBadgeOffline: "支持离线",
    heroBadgePlatforms: "Android / iOS / Web",
    selectWorkspace: "选择工作区",
    loadDemo: "加载演示",
    languageLabel: "语言",
    statusNoWorkspace: "尚未加载工作区。",
    androidIosPwa: "Android/iOS PWA",
    platformDetecting: "正在检测平台...",
    installHintPending: "页面在浏览器中加载后会显示安装提示。",
    offlineHintPending: "正在检查离线状态。",
    clearWorkspaceCache: "清除工作区缓存",
    summaryHeading: "概览",
    summaryProject: "项目",
    summaryQuestion: "问题",
    summaryDocuments: "文档",
    summaryExcerpts: "摘录",
    summaryReport: "报告",
    summaryProvider: "提供方",
    reportHeading: "报告",
    reportBadgeEmpty: "无报告",
    reportTitleEmpty: "尚未加载导出",
    reportPreviewEmpty: "导入工作区后即可在本地显示报告和元数据。",
    documentsHeading: "文档",
    documentListEmpty: "尚未加载文档。",
    reviewNotesHeading: "评审笔记",
    notesBadge: "本地保存",
    notesLabel: "你的观察、开放问题或移动端评审要点：",
    notesPlaceholder: "示例：更仔细检查第 3 节，并与昨天的报告进行来源对比 ...",
    exportNotes: "导出评审笔记",
    clearNotes: "清空笔记",
    cacheHintEmpty: "尚未为离线启动保存工作区。",
    cacheHintWithTitle: (title) => `上一个离线工作区：${title}。`,
    offlineStateOnline: "当前在线；新的导入可以缓存在本地。",
    offlineStateOffline: "当前离线；上次本地保存的工作区仍可使用。",
    noLeadQuestion: "无引导问题",
    selectedDocuments: (selected, total) => `已选择 ${selected} / ${total}`,
    excerptCount: (count) => `${count} 条摘录`,
    documentCount: (count) => `${count} 个条目`,
    reportContentEmpty: "导出中没有报告。",
    noDocumentsInExport: "导出中没有文档。",
    noExcerptsInExport: "导出中没有摘录。",
    excerptFallback: "摘录",
    selectedPill: "已选择",
    notSelectedPill: "未选择",
    unknownFormat: "未知",
    noPathHint: "无路径提示",
    contentIncluded: "包含内容",
    metadataOnly: "仅元数据",
    workspaceLoaded: (sourceLabel, title) => `${sourceLabel} 已加载：${title}`,
    loadWorkspaceFirst: "请先加载一个工作区。",
    notesExported: (filename) => `评审笔记已导出：${filename}`,
    notesCleared: "本地评审笔记已清空。",
    cacheCleared: "本地工作区缓存已清除。当前视图会保留到重新加载为止。",
    reviewFilenameSuffix: "review-notes",
    workspaceLoadErrorEmpty: "所选文件为空。",
    workspaceLoadErrorJson: "该文件不是有效的 JSON。",
    workspaceLoadErrorObject: "工作区必须是一个 JSON 对象。",
    workspaceLoadErrorSchema: (schemaVersion) => `不支持的架构版本：${schemaVersion}`,
    untitledWorkspace: "未命名工作区",
    untitledDocument: (index) => `文档 ${index + 1}`,
    reportDefaultTitle: "报告",
    providerUnknown: "未知",
    modeUnknown: "未知",
    reviewHeadingWithTitle: (title) => `# 评审笔记：${title}`,
    reviewExportedAt: "导出时间",
    reviewQuestion: "问题",
    reviewReport: "报告",
    reviewDocuments: "文档",
    reviewExcerpts: "摘录",
    reviewNotesSection: "## 笔记",
    reviewNotesEmpty: "_没有额外的评审笔记。_",
    sourceLabelDemo: "演示工作区",
    sourceLabelCached: "本地离线工作区",
    platformAndroidLabel: "Android",
    platformAndroidInstallHint: "在 Chrome 中，通过菜单或安装图标将应用添加到主屏幕。",
    platformAndroidOfflineHint: "首次导入后，最后加载的工作区会本地保存，之后可离线启动。",
    platformIosLabel: "iPhone / iPad",
    platformIosInstallHint: "在 Safari 中，通过分享 → 添加到主屏幕来保存 PWA。",
    platformIosOfflineHint: "首次导入后，最后加载的工作区即使没有网络也可再次打开。",
    platformBrowserLabel: "浏览器",
    platformBrowserInstallHint: "Companion 可在浏览器中运行；在 Android 或 iOS 上也可保存为 PWA。",
    platformBrowserOfflineHint: "如需离线启动，必须至少先在本地导入一个工作区。"
  }),
  ja: Object.freeze({
    pageTitle: "NoteSpaceLLM Web/PWA Companion",
    pageDescription: "NoteSpaceLLM からエクスポートしたワークスペース用のローカル Web/PWA Companion。モバイルレビュー用ノート、レポートプレビュー、文書メタデータをサーバーへアップロードせずに扱えます。",
    ogTitle: "NoteSpaceLLM Web/PWA Companion",
    ogDescription: "NoteSpaceLLM からエクスポートしたワークスペースを読むための読み取り専用ブラウザー Companion。レビュー用ノートはローカルに保存され、サーバーへアップロードされません。",
    eyebrow: "NoteSpaceLLM Companion",
    heroTitle: "エクスポート済みワークスペース用のローカルレビューリーダー",
    heroCopy: "Companion は notespacellm-workspace-v1.json をブラウザー内で直接インポートし、ワークスペースは読み取り専用のまま、あなたのレビュー用ノートだけをエクスポートします。",
    heroBadgePrivacy: "アップロードなし",
    heroBadgeOffline: "オフライン対応",
    heroBadgePlatforms: "Android / iOS / Web",
    selectWorkspace: "ワークスペースを選択",
    loadDemo: "デモを読み込む",
    languageLabel: "言語",
    statusNoWorkspace: "ワークスペースはまだ読み込まれていません。",
    androidIosPwa: "Android/iOS PWA",
    platformDetecting: "プラットフォームを検出中...",
    installHintPending: "ブラウザーでページを読み込むとインストール案内が表示されます。",
    offlineHintPending: "オフライン状態を確認しています。",
    clearWorkspaceCache: "ワークスペースキャッシュを削除",
    summaryHeading: "概要",
    summaryProject: "プロジェクト",
    summaryQuestion: "質問",
    summaryDocuments: "文書",
    summaryExcerpts: "抜粋",
    summaryReport: "レポート",
    summaryProvider: "プロバイダー",
    reportHeading: "レポート",
    reportBadgeEmpty: "レポートなし",
    reportTitleEmpty: "エクスポートはまだ読み込まれていません",
    reportPreviewEmpty: "ワークスペースをインポートすると、レポートとメタデータをローカルに表示できます。",
    documentsHeading: "文書",
    documentListEmpty: "文書はまだ読み込まれていません。",
    reviewNotesHeading: "レビュー用ノート",
    notesBadge: "ローカル保存",
    notesLabel: "あなたの観察、未解決の質問、モバイルレビューの要点：",
    notesPlaceholder: "例：第 3 節を詳しく確認し、昨日のレポートと出典を比較する ...",
    exportNotes: "レビュー用ノートをエクスポート",
    clearNotes: "ノートを消去",
    cacheHintEmpty: "オフライン起動用に保存されたワークスペースはまだありません。",
    cacheHintWithTitle: (title) => `最後のオフラインワークスペース：${title}。`,
    offlineStateOnline: "現在オンラインです。新しいインポートをローカルにキャッシュできます。",
    offlineStateOffline: "現在オフラインです。最後にローカル保存されたワークスペースは利用できます。",
    noLeadQuestion: "ガイド質問なし",
    selectedDocuments: (selected, total) => `${total} 件中 ${selected} 件を選択`,
    excerptCount: (count) => `${count} 件の抜粋`,
    documentCount: (count) => `${count} 件`,
    reportContentEmpty: "エクスポートにレポートは含まれていません。",
    noDocumentsInExport: "エクスポートに文書は含まれていません。",
    noExcerptsInExport: "エクスポートに抜粋は含まれていません。",
    excerptFallback: "抜粋",
    selectedPill: "選択済み",
    notSelectedPill: "未選択",
    unknownFormat: "不明",
    noPathHint: "パス情報なし",
    contentIncluded: "本文あり",
    metadataOnly: "メタデータのみ",
    workspaceLoaded: (sourceLabel, title) => `${sourceLabel} を読み込みました：${title}`,
    loadWorkspaceFirst: "先にワークスペースを読み込んでください。",
    notesExported: (filename) => `レビュー用ノートをエクスポートしました：${filename}`,
    notesCleared: "ローカルのレビュー用ノートを消去しました。",
    cacheCleared: "ローカルワークスペースキャッシュを削除しました。現在の表示は再読み込みまで残ります。",
    reviewFilenameSuffix: "review-notes",
    workspaceLoadErrorEmpty: "選択したファイルは空です。",
    workspaceLoadErrorJson: "このファイルは有効な JSON ではありません。",
    workspaceLoadErrorObject: "ワークスペースは JSON オブジェクトである必要があります。",
    workspaceLoadErrorSchema: (schemaVersion) => `サポートされていないスキーマバージョン：${schemaVersion}`,
    untitledWorkspace: "無題のワークスペース",
    untitledDocument: (index) => `文書 ${index + 1}`,
    reportDefaultTitle: "レポート",
    providerUnknown: "不明",
    modeUnknown: "不明",
    reviewHeadingWithTitle: (title) => `# レビュー用ノート：${title}`,
    reviewExportedAt: "エクスポート日時",
    reviewQuestion: "質問",
    reviewReport: "レポート",
    reviewDocuments: "文書",
    reviewExcerpts: "抜粋",
    reviewNotesSection: "## ノート",
    reviewNotesEmpty: "_追加のレビュー用ノートはありません。_",
    sourceLabelDemo: "デモワークスペース",
    sourceLabelCached: "ローカルオフラインワークスペース",
    platformAndroidLabel: "Android",
    platformAndroidInstallHint: "Chrome のメニューまたはインストールアイコンから、アプリをホーム画面に追加します。",
    platformAndroidOfflineHint: "最初のインポート後、最後に読み込んだワークスペースはローカルに保存され、あとでオフライン起動できます。",
    platformIosLabel: "iPhone / iPad",
    platformIosInstallHint: "Safari の共有 → ホーム画面に追加で PWA を保存します。",
    platformIosOfflineHint: "最初のインポート後、最後に読み込んだワークスペースはネットワークなしでも再度開けます。",
    platformBrowserLabel: "ブラウザー",
    platformBrowserInstallHint: "Companion はブラウザーで動作します。Android または iOS では PWA として保存することもできます。",
    platformBrowserOfflineHint: "オフライン起動には、少なくとも一度ワークスペースをローカルにインポートしておく必要があります。"
  }),
  ru: Object.freeze({
    pageTitle: "NoteSpaceLLM Web/PWA Companion",
    pageDescription: "Локальный Web/PWA Companion для экспортированных рабочих пространств NoteSpaceLLM: мобильные заметки для ревью, предпросмотр отчета и метаданные документов без загрузки на сервер.",
    ogTitle: "NoteSpaceLLM Web/PWA Companion",
    ogDescription: "Браузерный companion только для чтения экспортированных рабочих пространств NoteSpaceLLM с локальными заметками для ревью и без загрузки на сервер.",
    eyebrow: "NoteSpaceLLM Companion",
    heroTitle: "Локальный ридер ревью для экспортированных рабочих пространств",
    heroCopy: "Companion импортирует notespacellm-workspace-v1.json прямо в браузере, оставляет рабочее пространство только для чтения и экспортирует только ваши заметки для ревью.",
    heroBadgePrivacy: "Без загрузки",
    heroBadgeOffline: "Работает офлайн",
    heroBadgePlatforms: "Android / iOS / Web",
    selectWorkspace: "Выбрать workspace",
    loadDemo: "Загрузить демо",
    languageLabel: "Язык",
    statusNoWorkspace: "Рабочее пространство еще не загружено.",
    androidIosPwa: "Android/iOS PWA",
    platformDetecting: "Определение платформы...",
    installHintPending: "Подсказки по установке появятся после загрузки страницы в браузере.",
    offlineHintPending: "Проверка офлайн-статуса.",
    clearWorkspaceCache: "Очистить кэш workspace",
    summaryHeading: "Обзор",
    summaryProject: "Проект",
    summaryQuestion: "Вопрос",
    summaryDocuments: "Документы",
    summaryExcerpts: "Фрагменты",
    summaryReport: "Отчет",
    summaryProvider: "Провайдер",
    reportHeading: "Отчет",
    reportBadgeEmpty: "Нет отчета",
    reportTitleEmpty: "Экспорт еще не загружен",
    reportPreviewEmpty: "Импортируйте workspace, чтобы локально показать отчет и метаданные.",
    documentsHeading: "Документы",
    documentListEmpty: "Документы еще не загружены.",
    reviewNotesHeading: "Заметки для ревью",
    notesBadge: "Сохраняется локально",
    notesLabel: "Ваши наблюдения, открытые вопросы или пункты мобильного ревью:",
    notesPlaceholder: "Пример: подробнее проверить раздел 3, сравнить источники с отчетом за вчера ...",
    exportNotes: "Экспортировать заметки",
    clearNotes: "Очистить заметки",
    cacheHintEmpty: "Пока нет workspace, сохраненного для офлайн-запуска.",
    cacheHintWithTitle: (title) => `Последний офлайн-workspace: ${title}.`,
    offlineStateOnline: "Сейчас онлайн; новый импорт можно локально закэшировать.",
    offlineStateOffline: "Сейчас офлайн; последний локально сохраненный workspace остается доступным.",
    noLeadQuestion: "Нет направляющего вопроса",
    selectedDocuments: (selected, total) => `выбрано ${selected} из ${total}`,
    excerptCount: (count) => `${count} фрагментов`,
    documentCount: (count) => `${count} элементов`,
    reportContentEmpty: "В экспорте нет отчета.",
    noDocumentsInExport: "В экспорте нет документов.",
    noExcerptsInExport: "В экспорте нет фрагментов.",
    excerptFallback: "Фрагмент",
    selectedPill: "Выбрано",
    notSelectedPill: "Не выбрано",
    unknownFormat: "неизвестно",
    noPathHint: "без подсказки пути",
    contentIncluded: "содержимое включено",
    metadataOnly: "только метаданные",
    workspaceLoaded: (sourceLabel, title) => `${sourceLabel} загружен: ${title}`,
    loadWorkspaceFirst: "Сначала загрузите workspace.",
    notesExported: (filename) => `Заметки для ревью экспортированы: ${filename}`,
    notesCleared: "Локальные заметки для ревью очищены.",
    cacheCleared: "Локальный кэш workspace очищен. Текущий вид останется до перезагрузки.",
    reviewFilenameSuffix: "review-notes",
    workspaceLoadErrorEmpty: "Выбранный файл пуст.",
    workspaceLoadErrorJson: "Файл не является допустимым JSON.",
    workspaceLoadErrorObject: "Workspace должен быть JSON-объектом.",
    workspaceLoadErrorSchema: (schemaVersion) => `Неподдерживаемая версия схемы: ${schemaVersion}`,
    untitledWorkspace: "Безымянный workspace",
    untitledDocument: (index) => `Документ ${index + 1}`,
    reportDefaultTitle: "Отчет",
    providerUnknown: "неизвестно",
    modeUnknown: "неизвестно",
    reviewHeadingWithTitle: (title) => `# Заметки для ревью: ${title}`,
    reviewExportedAt: "Экспортировано",
    reviewQuestion: "Вопрос",
    reviewReport: "Отчет",
    reviewDocuments: "Документы",
    reviewExcerpts: "Фрагменты",
    reviewNotesSection: "## Заметки",
    reviewNotesEmpty: "_Дополнительных заметок для ревью нет._",
    sourceLabelDemo: "Демо-workspace",
    sourceLabelCached: "Локальный офлайн-workspace",
    platformAndroidLabel: "Android",
    platformAndroidInstallHint: "В Chrome используйте меню или значок установки, чтобы добавить приложение на главный экран.",
    platformAndroidOfflineHint: "После первого импорта последний загруженный workspace сохраняется локально для последующего офлайн-запуска.",
    platformIosLabel: "iPhone / iPad",
    platformIosInstallHint: "В Safari используйте Поделиться → На экран «Домой», чтобы сохранить PWA.",
    platformIosOfflineHint: "После первого импорта последний загруженный workspace можно снова открыть даже без сети.",
    platformBrowserLabel: "Браузер",
    platformBrowserInstallHint: "Companion работает в браузере; на Android или iOS его также можно сохранить как PWA.",
    platformBrowserOfflineHint: "Для офлайн-запуска нужно хотя бы один раз локально импортировать workspace."
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
  if (candidate.startsWith("es")) {
    return "es";
  }
  if (candidate.startsWith("zh")) {
    return "zh-Hans";
  }
  if (candidate.startsWith("ja")) {
    return "ja";
  }
  if (candidate.startsWith("ru")) {
    return "ru";
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
  const demo = {
    de: {
      title: "Demo: Forschungsnotizen",
      question: "Welche Kernthesen tragen den Bericht am stärksten?",
      firstName: "berichtsentwurf.md",
      firstPath: "berichte/berichtsentwurf.md",
      firstExcerpt: "Die stärkste Evidenz liegt in der Kombination aus Primärquelle und Gegenprüfung.",
      firstSource: "Abschnitt 2",
      secondName: "literatur.pdf",
      secondPath: "quellen/literatur.pdf",
      secondExcerpt: "Mehrere Studien weisen auf denselben methodischen Engpass hin.",
      secondSource: "Seite 14",
      reportTitle: "Synthesebericht",
      reportContent: "# Synthese\n\n- Kernthese A wird durch zwei Quellen gestützt.\n- Offene Lücke: Vergleichsdaten für 2024 fehlen noch.",
      assistantMessage: "Fasse die Quellenlage für die Hauptthese zusammen."
    },
    en: {
      title: "Demo: research notes",
      question: "Which core claims carry the report most strongly?",
      firstName: "report-draft.md",
      firstPath: "reports/report-draft.md",
      firstExcerpt: "The strongest evidence comes from combining the primary source with an explicit cross-check.",
      firstSource: "Section 2",
      secondName: "literature.pdf",
      secondPath: "sources/literature.pdf",
      secondExcerpt: "Several studies point to the same methodological bottleneck.",
      secondSource: "Page 14",
      reportTitle: "Synthesis report",
      reportContent: "# Synthesis\n\n- Core claim A is supported by two sources.\n- Open gap: comparative data for 2024 is still missing.",
      assistantMessage: "Summarize the evidence base for the main claim."
    },
    es: {
      title: "Demo: notas de investigación",
      question: "¿Qué tesis centrales sostienen con más fuerza el informe?",
      firstName: "borrador-informe.md",
      firstPath: "informes/borrador-informe.md",
      firstExcerpt: "La evidencia más fuerte surge al combinar la fuente primaria con una comprobación explícita.",
      firstSource: "Sección 2",
      secondName: "literatura.pdf",
      secondPath: "fuentes/literatura.pdf",
      secondExcerpt: "Varios estudios apuntan al mismo cuello de botella metodológico.",
      secondSource: "Página 14",
      reportTitle: "Informe de síntesis",
      reportContent: "# Síntesis\n\n- La tesis central A está respaldada por dos fuentes.\n- Brecha abierta: aún faltan datos comparativos para 2024.",
      assistantMessage: "Resume la base de evidencia de la tesis principal."
    },
    "zh-Hans": {
      title: "演示：研究笔记",
      question: "哪些核心论点最有力地支撑这份报告？",
      firstName: "report-draft.md",
      firstPath: "reports/report-draft.md",
      firstExcerpt: "最有力的证据来自将一手资料与明确的交叉核查结合起来。",
      firstSource: "第 2 节",
      secondName: "literature.pdf",
      secondPath: "sources/literature.pdf",
      secondExcerpt: "多项研究都指向同一个方法瓶颈。",
      secondSource: "第 14 页",
      reportTitle: "综合报告",
      reportContent: "# 综合\n\n- 核心论点 A 得到两个来源的支持。\n- 未解决缺口：仍缺少 2024 年的比较数据。",
      assistantMessage: "总结主要论点的证据基础。"
    },
    ja: {
      title: "デモ：研究ノート",
      question: "どの中心的な主張がレポートを最も強く支えていますか？",
      firstName: "report-draft.md",
      firstPath: "reports/report-draft.md",
      firstExcerpt: "最も強い証拠は、一次資料と明示的なクロスチェックを組み合わせることから得られます。",
      firstSource: "第 2 節",
      secondName: "literature.pdf",
      secondPath: "sources/literature.pdf",
      secondExcerpt: "複数の研究が同じ方法論上のボトルネックを示しています。",
      secondSource: "14 ページ",
      reportTitle: "統合レポート",
      reportContent: "# 統合\n\n- 中心的主張 A は 2 つの出典に支えられています。\n- 未解決のギャップ：2024 年の比較データがまだ不足しています。",
      assistantMessage: "主張の根拠となる証拠を要約してください。"
    },
    ru: {
      title: "Демо: исследовательские заметки",
      question: "Какие ключевые тезисы сильнее всего поддерживают отчет?",
      firstName: "report-draft.md",
      firstPath: "reports/report-draft.md",
      firstExcerpt: "Самые сильные доказательства возникают при сочетании первичного источника с явной перекрестной проверкой.",
      firstSource: "Раздел 2",
      secondName: "literature.pdf",
      secondPath: "sources/literature.pdf",
      secondExcerpt: "Несколько исследований указывают на одно и то же методологическое узкое место.",
      secondSource: "Страница 14",
      reportTitle: "Синтетический отчет",
      reportContent: "# Синтез\n\n- Ключевой тезис A подтверждается двумя источниками.\n- Открытый пробел: сравнительные данные за 2024 год все еще отсутствуют.",
      assistantMessage: "Суммируй доказательную базу по главному тезису."
    }
  }[resolvedLocale];

  const demoPayload = {
    schema_version: "notespacellm-workspace-v1",
    app: {
      name: "NoteSpaceLLM",
      version: "1.0.0",
      exported_at: "2026-05-28T10:00:00Z"
    },
    workspace: {
      title: demo.title,
      question: demo.question,
      workflow_type: "research",
      locale: resolvedLocale
    },
    documents: [
      {
        id: "doc-1",
        name: demo.firstName,
        path_hint: demo.firstPath,
        format: "markdown",
        selected: true,
        content_included: false,
        excerpts: [
          {
            id: "doc-1-excerpt-1",
            text: demo.firstExcerpt,
            source_hint: demo.firstSource
          }
        ]
      },
      {
        id: "doc-2",
        name: demo.secondName,
        path_hint: demo.secondPath,
        format: "pdf",
        selected: true,
        content_included: false,
        excerpts: [
          {
            id: "doc-2-excerpt-1",
            text: demo.secondExcerpt,
            source_hint: demo.secondSource
          }
        ]
      }
    ],
    report: {
      title: demo.reportTitle,
      format: "markdown",
      content: demo.reportContent
    },
    chat: {
      messages: [
        {
          role: "assistant",
          content: demo.assistantMessage
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
