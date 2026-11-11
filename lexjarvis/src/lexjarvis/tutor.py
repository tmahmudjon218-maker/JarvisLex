"""Claude-powered tutor that answers and quizzes strictly from local sources."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Any

from .knowledge import Chunk, KnowledgeBase
from .prompts import NO_SOURCE_MESSAGE, QUIZ_SYSTEM_PROMPT, SYSTEM_PROMPT

DEFAULT_MODEL = "claude-sonnet-5-5"


@dataclass
class Answer:
    text: str
    sources: list[str] = field(default_factory=list)
    grounded: bool = True


@dataclass
class QuizQuestion:
    question: str
    options: list[str]
    answer: int
    explanation: str
    source: str = ""


def format_sources(hits: list[tuple[Chunk, float]]) -> str:
    blocks = []
    for chunk, _score in hits:
        blocks.append(
            f'<manba id="{chunk.ref}" sarlavha="{chunk.heading}">\n{chunk.text}\n</manba>'
        )
    return "\n\n".join(blocks)


def parse_quiz_json(raw: str) -> list[QuizQuestion]:
    """Parse and validate the model's JSON quiz output, tolerating code fences."""
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())
    start, end = cleaned.find("["), cleaned.rfind("]")
    if start == -1 or end == -1:
        raise ValueError("Model JSON massiv qaytarmadi")
    data = json.loads(cleaned[start : end + 1])
    questions: list[QuizQuestion] = []
    for item in data:
        options = item.get("options", [])
        answer = item.get("answer")
        if len(options) != 4 or not isinstance(answer, int) or not 0 <= answer < 4:
            continue  # skip malformed questions instead of failing the whole quiz
        questions.append(
            QuizQuestion(
                question=str(item["question"]),
                options=[str(o) for o in options],
                answer=answer,
                explanation=str(item.get("explanation", "")),
                source=str(item.get("source", "")),
            )
        )
    if not questions:
        raise ValueError("Yaroqli savollar topilmadi")
    return questions


def _text_of(response: Any) -> str:
    return "".join(
        block.text for block in response.content if getattr(block, "type", "") == "text"
    ).strip()


class Tutor:
    def __init__(
        self,
        kb: KnowledgeBase,
        client: Any | None = None,
        model: str | None = None,
        max_tokens: int = 1500,
    ) -> None:
        self.kb = kb
        self._client = client
        self.model = model or os.environ.get("LEXJARVIS_MODEL", DEFAULT_MODEL)
        self.max_tokens = max_tokens

    @property
    def client(self) -> Any:
        if self._client is None:
            import anthropic  # lazy: tests and `--help` work without a key

            self._client = anthropic.Anthropic()
        return self._client

    def ask(self, question: str, history: list[dict[str, str]] | None = None) -> Answer:
        hits = self.kb.search(question)
        if not hits:
            return Answer(NO_SOURCE_MESSAGE, [], grounded=False)
        user = f"{format_sources(hits)}\n\nSavol: {question}"
        messages = [*(history or []), {"role": "user", "content": user}]
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=SYSTEM_PROMPT,
            messages=messages,
        )
        return Answer(_text_of(response), [c.ref for c, _ in hits])

    def quiz(self, topic: str, n: int = 5) -> list[QuizQuestion]:
        hits = self.kb.search(topic, top_k=6)
        if not hits:
            raise LookupError(NO_SOURCE_MESSAGE)
        user = f"{format_sources(hits)}\n\nMavzu: {topic}\nSavollar soni: {n}"
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens * 2,
            system=QUIZ_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user}],
        )
        return parse_quiz_json(_text_of(response))[:n]
