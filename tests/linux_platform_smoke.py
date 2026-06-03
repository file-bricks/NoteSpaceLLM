#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reproduzierbarer Linux-Source-Smoke für NoteSpaceLLM.

Prüft auf Linux:
- offscreen PySide6-Start
- Dokumentimport mit echten Umlauten
- einfachen Berichtsexport nach Markdown und TXT
- Workspace-Export für den Web/PWA-Companion
"""

from __future__ import annotations

import sys

from platform_smoke import run_platform_smoke


def main() -> int:
    if not sys.platform.startswith("linux"):
        raise SystemExit("Dieser Smoke ist nur für Linux gedacht.")

    summary = run_platform_smoke(project_name="Linux Smoke")
    print(f"Linux platform smoke OK: {summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
