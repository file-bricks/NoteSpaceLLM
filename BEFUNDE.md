# Offene Befunde — NoteSpaceLLM

**Erfasst am:** 2026-07-28  
**Rolle:** MAINTAINER (TaskMaster Loop)

---

### Befund 1: Uncommitted & Untracked Assets in web_companion/

- **Fundort:** `web_companion/`
- **Beleg:**  
  `git status` zeigt 6 modifizierte Icon/Manifest-Dateien und 9 ungetrackte Icon-Dateien.
- **Vorschlag:**  
  TASKSOLVER soll prüfen, ob die `web_companion`-Assets committet werden sollen (`git add`).

---

---

### Befund 3: Test-Fehlschlag (`test_store_readiness.py`)

- **Fundort:** `tests/test_store_readiness.py::test_releases_windowsstore_files`
- **Beleg:**  
  `AssertionError: releases/windowsstore directory missing` (`C:\_Local_DEV\repos\NoteSpaceLLM\releases\windowsstore`).
- **Vorschlag:**  
  TASKSOLVER soll das Verzeichnis `releases/windowsstore` anlegen/anpassen oder die Test-Bedingung in `test_store_readiness.py` prüfen.
