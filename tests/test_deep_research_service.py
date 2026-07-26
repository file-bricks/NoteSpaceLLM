#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for Deep Research Service (TW-NSLLM-03)
==============================================
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.core.researcher import ResearchService, DeepResearchResult
from src.core.sub_query import SubQueryManager, SubQueryStatus
from src.reports.templates import get_template, TEMPLATES


class MockLLMClient:
    def __init__(self, mock_response="Das Dokument analysiert relevante Sicherheits- und Architekturkonzepte."):
        self.mock_response = mock_response
        self.calls = []

    def chat(self, prompt: str, system_prompt: str = "") -> str:
        self.calls.append((prompt, system_prompt))
        return self.mock_response


class TestDeepResearchService(unittest.TestCase):

    def test_deep_research_template_registration(self):
        """Prüft, ob das deep_research Template registriert ist."""
        self.assertIn("deep_research", TEMPLATES)
        template = get_template("deep_research")
        self.assertIsNotNone(template)
        self.assertEqual(template.id, "deep_research")
        self.assertEqual(len(template.sections), 5)
        section_ids = [s.id for s in template.sections]
        self.assertEqual(section_ids, ["plan", "definitions", "implications", "gaps", "summary"])

    def test_generate_plan_fallback(self):
        """Prüft die Generierung des Standard-Forschungsplans ohne LLM."""
        service = ResearchService()
        plan = service.generate_plan("Künstliche Intelligenz in der Medizin")
        self.assertEqual(len(plan), 5)
        self.assertEqual(plan[0]["aspect"], "Begriffe & Grundlagen")
        self.assertIn("Künstliche Intelligenz in der Medizin", plan[0]["question"])

    def test_generate_plan_with_mock_llm(self):
        """Prüft die Generierung des Forschungsplans mit LLM-Antwort."""
        custom_llm_response = (
            "1. Definitionen: Welche Begriffe werden definiert?\n"
            "2. Datenquellen: Welche Datensätze werden genannt?\n"
            "3. Methodik: Welche KI-Modelle kommen zum Einsatz?\n"
            "4. Ergebnisse: Welche Genauigkeit wird erzielt?\n"
            "5. Fazit: Welche Hauptaussage wird getroffen?"
        )
        llm = MockLLMClient(custom_llm_response)
        service = ResearchService(llm_client=llm)
        plan = service.generate_plan("KI-Modelle")
        self.assertEqual(len(plan), 5)
        self.assertEqual(plan[0]["aspect"], "Definitionen")
        self.assertEqual(plan[2]["aspect"], "Methodik")

    def test_deep_dive_execution(self):
        """Prüft die vollständige Durchführung der Deep-Dive-Recherche."""
        llm = MockLLMClient("Befund: Das Dokument liefert konkrete Evidenz.")
        subquery_mgr = SubQueryManager()
        service = ResearchService(llm_client=llm)

        progress_steps = []
        def progress_cb(stage, step, total):
            progress_steps.append((stage, step, total))

        result = service.deep_dive(
            doc_id="doc_123",
            doc_title="Sicherheitskonzept 2026.pdf",
            doc_text="Inhalt des Sicherheitskonzepts...",
            topic="Verschlüsselung und Zugriffssteuerung",
            subquery_manager=subquery_mgr,
            progress_callback=progress_cb
        )

        self.assertIsInstance(result, DeepResearchResult)
        self.assertEqual(result.topic, "Verschlüsselung und Zugriffssteuerung")
        self.assertEqual(result.document_id, "doc_123")
        self.assertEqual(result.document_title, "Sicherheitskonzept 2026.pdf")
        self.assertEqual(len(result.findings), 5)
        self.assertIn("Deep Research Bericht", result.markdown)
        self.assertIn("Sicherheitskonzept 2026.pdf", result.markdown)
        self.assertIn("3. Gesamtfazit & Synthese", result.markdown)

        # Prüfe eingetragene SubQueries
        queries = subquery_mgr.get_queries_for_document("doc_123")
        self.assertEqual(len(queries), 5)
        for q in queries:
            self.assertEqual(q.status, SubQueryStatus.COMPLETED)
            self.assertIn("Verschlüsselung und Zugriffssteuerung", q.query_text)

        # Prüfe Progress Callback
        self.assertEqual(len(progress_steps), 7)
        self.assertEqual(progress_steps[0][0], "Forschungsplan erstellen")
        self.assertEqual(progress_steps[-1][0], "Gesamtfazit synthetisieren")

    def test_result_to_dict(self):
        """Prüft die Serialisierung von DeepResearchResult."""
        result = DeepResearchResult(
            topic="Test-Thema",
            document_id="doc_1",
            document_title="Test.txt",
            plan=[{"aspect": "A1", "question": "Q1"}],
            findings=[{"aspect": "A1", "question": "Q1", "answer": "Ans1"}],
            summary="Fazit",
            markdown="# Test"
        )
        d = result.to_dict()
        self.assertEqual(d["topic"], "Test-Thema")
        self.assertEqual(d["summary"], "Fazit")
        self.assertEqual(len(d["plan"]), 1)


if __name__ == "__main__":
    unittest.main()
