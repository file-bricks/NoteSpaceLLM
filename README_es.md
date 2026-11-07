<img src="assets/banner.svg" width="100%" alt="NoteSpaceLLM Banner">

[English](README.md) · [Deutsch](README_de.md) · [Español](README_es.md) · [简体中文](README_zh.md) · [日本語](README_ja.md) · [Русский](README_ru.md)

# NoteSpaceLLM Pro

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Platform: Windows](https://img.shields.io/badge/platform-Windows-lightgrey.svg)]()
[![Offline-first](https://img.shields.io/badge/offline--first-yes-green.svg)]()

> **Alternativa local a NotebookLM para análisis privado de documentos, investigación asistida por RAG y generación de informes multiformato.**

NoteSpaceLLM Pro es su estación de trabajo privada y local para el análisis estructurado de documentos, la gestión inteligente de notas y la investigación asistida por inteligencia artificial. Como alternativa enfocada en la privacidad frente a los servicios en la nube, NoteSpaceLLM mantiene todos los documentos e índices vectoriales en su propio equipo.

Permite analizar archivos PDF, documentos de Word, notas en Markdown, exportaciones de correo y carpetas de investigación. Funciona sin conexión con modelos locales (p. ej. mediante Ollama) o con APIs seguras (Anthropic Claude, OpenAI). Los resultados se pueden exportar a Markdown, PDF, DOCX, HTML y TXT. Incluye un compañero Web/PWA ligero para revisar espacios de trabajo en Android, iOS y navegadores sin subir datos a ningún servidor.

## Inicio rápido

```bash
git clone https://github.com/file-bricks/NoteSpaceLLM.git
cd NoteSpaceLLM
pip install -r requirements.txt
python main.py
```

En Windows también puede iniciarse mediante `start.bat`. Para compilar un ejecutable independiente, utilice `build_exe.bat`.

Ejecutar pruebas y comprobaciones de compilación:

```bash
python -m pytest -q
python manage_translations.py --check
python scripts/check_store_readiness.py
python -m compileall -q main.py manage_translations.py translator.py src
```

## Características destacadas

- **Gestión documental**: Importación de archivos y carpetas mediante arrastrar y soltar
- **Indexación automática**: Procesamiento inmediato para búsquedas vectoriales RAG
- **Selección granular**: Activar o excluir documentos de los informes de forma individual
- **Consultas específicas**: Preguntas dirigidas a documentos concretos con clic derecho
- **Visualización de flujo**: Esquema gráfico de toda la secuencia de análisis
- **Chat interactivo**: Conversación contextual sobre su documentación con cualquier LLM
- **Investigación profunda (Deep Research)**: Informes de síntesis y resúmenes automáticos
- **Exportación versátil**: Salida en Markdown, PDF, DOCX, HTML y texto plano
- **Exportación de prompts**: Guarda el contexto del informe como prompt para flujos externos
- **Soporte de 6 idiomas (Tier-2)**: Interfaz y metadatos en DE, EN, ES, ZH, JA y RU
- **Privacidad y Zero-Egress**: Base de datos vectorial local (ChromaDB) sin transferencias forzadas

## Licencia y Privacidad

NoteSpaceLLM está licenciado bajo **AGPL-3.0**. Todos los análisis e índices vectoriales permanecen exclusivamente en su almacenamiento local.
