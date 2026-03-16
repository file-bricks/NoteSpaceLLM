#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NoteSpaceLLM - Private NotebookLM Clone for Report Generation
=============================================================

A local-first document analysis and report generation tool.

Usage:
    python main.py              # Start GUI
    python main.py --cli        # CLI mode (future)
    python main.py --help       # Show help
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def check_dependencies():
    """Check if required dependencies are available."""
    missing = []

    try:
        from PySide6.QtWidgets import QApplication
    except ImportError:
        missing.append("PyQt6 (pip install PyQt6)")

    # Optional but recommended
    optional_missing = []

    try:
        from docx import Document
    except ImportError:
        optional_missing.append("python-docx (for DOCX export)")

    try:
        import fitz
    except ImportError:
        optional_missing.append("PyMuPDF (for PDF reading)")

    try:
        import openpyxl
    except ImportError:
        optional_missing.append("openpyxl (for Excel support)")

    if missing:
        print("FEHLER: Fehlende Abhaengigkeiten:")
        for dep in missing:
            print(f"  - {dep}")
        print("\nInstalliere mit: pip install -r requirements.txt")
        return False

    if optional_missing:
        print("HINWEIS: Optionale Abhaengigkeiten nicht installiert:")
        for dep in optional_missing:
            print(f"  - {dep}")
        print()

    return True


def main():
    """Main entry point."""
    # Parse arguments
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        print("\nOptionen:")
        print("  --help, -h     Diese Hilfe anzeigen")
        print("  --version      Version anzeigen")
        print("  --check        Abhaengigkeiten pruefen")
        return

    if "--version" in sys.argv:
        from src import __version__
        print(f"NoteSpaceLLM v{__version__}")
        return

    if "--check" in sys.argv:
        check_dependencies()
        return

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Start GUI
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
    from src.gui.main_window import MainWindow

    # High DPI support
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("NoteSpaceLLM")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("BACH")

    # Set style
    app.setStyle("Fusion")

    # Create and show main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
