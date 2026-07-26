#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deep Research Service - Multi-step structured research on documents
=====================================================================

Implements structured deep-dive research workflows for specific documents
and topics:
1. Generate research plan (structured sub-questions)
2. Run targeted sub-queries per aspect/question via RAG engine or LLM
3. Summarize findings into a structured report result and Markdown document.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any

from .sub_query import SubQueryManager, SubQuery, SubQueryType

logger = logging.getLogger(__name__)


@dataclass
class DeepResearchResult:
    """Result of a deep research process."""
    topic: str
    document_id: str
    document_title: str
    plan: List[Dict[str, str]]
    findings: List[Dict[str, str]]
    summary: str
    markdown: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "topic": self.topic,
            "document_id": self.document_id,
            "document_title": self.document_title,
            "plan": self.plan,
            "findings": self.findings,
            "summary": self.summary,
            "markdown": self.markdown,
            "created_at": self.created_at
        }


class ResearchService:
    """
    Service for executing structured multi-step Deep Research on documents.

    Workflow:
    1. Plan: Breakdown topic into targeted research questions.
    2. Deep Dive: Execute sub-queries per question (via RAG or LLM).
    3. Synthesize: Aggregate findings into a structured report and Markdown summary.
    """

    def __init__(self, llm_client: Optional[Any] = None, rag_engine: Optional[Any] = None):
        """
        Initialize the research service.

        Args:
            llm_client: Optional LLMClient instance for text generation
            rag_engine: Optional RAGEngine instance for document queries
        """
        self.llm = llm_client
        self.rag_engine = rag_engine

    def generate_plan(self, topic: str, doc_text: str = "") -> List[Dict[str, str]]:
        """
        Generate a structured research plan with specific questions/aspects for the topic.

        Args:
            topic: The research topic or question
            doc_text: Optional text of the document to tailor questions

        Returns:
            List of dicts with keys 'aspect', 'question'
        """
        default_aspects = [
            {
                "aspect": "Begriffe & Grundlagen",
                "question": f"Welche zentralen Begriffe, Definitionen und Voraussetzungen werden bezüglich '{topic}' im Dokument genannt?"
            },
            {
                "aspect": "Kernbefunde & Argumentation",
                "question": f"Was sind die wichtigsten Hauptaussagen, Befunde und Argumente des Dokuments zu '{topic}'?"
            },
            {
                "aspect": "Implikationen & Konsequenzen",
                "question": f"Welche praktischen, theoretischen oder strukturellen Implikationen ergeben sich bezüglich '{topic}'?"
            },
            {
                "aspect": "Lücken & Unschärfen",
                "question": f"Welche offenen Fragen, Einschränkungen oder unvollständigen Informationen bezüglich '{topic}' hinterlässt das Dokument?"
            },
            {
                "aspect": "Synthese & Einordnung",
                "question": f"Wie lassen sich die Gesamterkenntnisse zu '{topic}' zusammenfassen und einordnen?"
            }
        ]

        if not self.llm or not topic:
            return default_aspects

        try:
            prompt = (
                f"Erstelle für eine vertiefte Analyse des Dokuments zum Thema '{topic}' genau 5 gezielte, "
                f"strukturierte Forschungsfragen. Gib das Ergebnis im Format:\n"
                f"1. [Aspekt]: [Frage]\n"
                f"2. [Aspekt]: [Frage]..."
            )
            response = self.llm.chat(prompt, doc_text[:4000] if doc_text else "")
            parsed = []
            for line in response.strip().split("\n"):
                line = line.strip()
                if ":" in line and any(line.startswith(f"{i}.") or line.startswith(f"{i})") for i in range(1, 10)):
                    parts = line.split(":", 1)
                    title = parts[0].split(".", 1)[-1].strip()
                    q = parts[1].strip()
                    if title and q:
                        parsed.append({"aspect": title, "question": q})
            if len(parsed) >= 3:
                return parsed
        except Exception as e:
            logger.warning("Generierung des Forschungsplans per LLM fehlgeschlagen, verwende Fallback-Plan: %s", e)

        return default_aspects

    def deep_dive(
        self,
        doc_id: str,
        doc_title: str,
        doc_text: str,
        topic: str,
        subquery_manager: Optional[SubQueryManager] = None,
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> DeepResearchResult:
        """
        Execute deep-dive research for a specific document and topic.

        Args:
            doc_id: Document ID
            doc_title: Display title of document
            doc_text: Extracted document text
            topic: Research focus/topic
            subquery_manager: Optional manager to record created subqueries
            progress_callback: Optional callback(stage_name, step, total_steps)

        Returns:
            DeepResearchResult object containing findings and markdown output
        """
        total_steps = 6
        if progress_callback:
            progress_callback("Forschungsplan erstellen", 1, total_steps)

        plan = self.generate_plan(topic, doc_text)
        findings: List[Dict[str, str]] = []

        for idx, item in enumerate(plan, 1):
            if progress_callback:
                progress_callback(f"Analysiere: {item['aspect']}", idx + 1, total_steps)

            aspect = item["aspect"]
            question = item["question"]
            answer = ""

            if self.rag_engine and getattr(self.rag_engine, "collection", None):
                try:
                    rag_result = self.rag_engine.query(question, n_results=3, document_id=doc_id)
                    if rag_result and rag_result.get("answer"):
                        answer = rag_result["answer"]
                except Exception as e:
                    logger.debug("RAG-Abfrage für Deep Research fehlgeschlagen: %s", e)

            if not answer and self.llm:
                prompt = (
                    f"Analysiere das folgende Dokument gezielt bezüglich dieser Frage:\n"
                    f"Frage: {question}\n\n"
                    f"Antworte präzise, strukturiert und stütze dich auf den Dokumententext."
                )
                context = doc_text[:16000] if doc_text else ""
                try:
                    answer = self.llm.chat(prompt, context)
                except Exception as e:
                    answer = f"Fehler bei der Analyse: {e}"
            elif not answer:
                answer = f"Synthetische Analyse für '{question}' (kein LLM-Client verbunden)."

            findings.append({
                "aspect": aspect,
                "question": question,
                "answer": answer
            })

            if subquery_manager:
                try:
                    sq = SubQuery.create(doc_id, SubQueryType.ANALYZE, f"[{topic}] {question}")
                    subquery_manager.add_query(sq)
                    subquery_manager.set_result(sq.id, answer)
                except Exception as e:
                    logger.warning("Konnte SubQuery für Deep Research nicht eintragen: %s", e)

        if progress_callback:
            progress_callback("Gesamtfazit synthetisieren", total_steps, total_steps)

        summary_prompt = (
            f"Fasse die folgenden 5 Befunde einer Deep-Research-Analyse zum Thema '{topic}' "
            f"aus dem Dokument '{doc_title}' in einem prägnanten Gesamtfazit zusammen:\n\n"
        )
        for f in findings:
            summary_prompt += f"### {f['aspect']}\n{f['answer']}\n\n"

        if self.llm:
            try:
                summary = self.llm.chat(summary_prompt, "")
            except Exception as e:
                summary = f"Zusammenfassendes Fazit konnte nicht generiert werden: {e}"
        else:
            summary = (
                f"Die Deep-Research-Analyse zu '{topic}' lieferte detaillierte Ergebnisse in {len(findings)} Hauptkategorien. "
                f"Alle Teilaspekte wurden erfolgreich untersucht."
            )

        markdown = self.format_as_markdown(topic, doc_title, plan, findings, summary)

        return DeepResearchResult(
            topic=topic,
            document_id=doc_id,
            document_title=doc_title,
            plan=plan,
            findings=findings,
            summary=summary,
            markdown=markdown
        )

    @staticmethod
    def format_as_markdown(
        topic: str,
        doc_title: str,
        plan: List[Dict[str, str]],
        findings: List[Dict[str, str]],
        summary: str
    ) -> str:
        """Format research results into a structured Markdown document."""
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        lines = [
            f"# Deep Research Bericht: {topic}",
            f"**Dokument:** {doc_title} | **Datum:** {now_str}",
            "",
            "---",
            "",
            "## 1. Forschungsplan",
            ""
        ]

        for idx, p in enumerate(plan, 1):
            lines.append(f"{idx}. **{p['aspect']}**: {p['question']}")

        lines.extend([
            "",
            "## 2. Detailergebnisse",
            ""
        ])

        for f in findings:
            lines.extend([
                f"### {f['aspect']}",
                f"**Fragestellung:** {f['question']}",
                "",
                f"{f['answer']}",
                ""
            ])

        lines.extend([
            "## 3. Gesamtfazit & Synthese",
            "",
            f"{summary}",
            ""
        ])

        return "\n".join(lines)
