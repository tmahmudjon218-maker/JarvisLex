"""Lightweight, dependency-free retrieval over local legal study materials.

Sources are plain ``.md`` / ``.txt`` files. They are split into chunks (by heading and
size) and ranked with BM25. Uzbek is agglutinative, so tokens are crudely truncated to a
fixed-length prefix, which lets "qonunlar" match "qonun". Replacing this with a real
stemmer or embeddings is a good first contribution (see CONTRIBUTING.md).
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

SUPPORTED_SUFFIXES = {".md", ".txt"}
STEM_LEN = 6

_APOSTROPHES = str.maketrans({"ʻ": "'", "ʼ": "'", "’": "'", "‘": "'", "`": "'"})
_TOKEN = re.compile(r"\w+(?:'\w+)*", re.UNICODE)


def tokenize(text: str) -> list[str]:
    """Lowercase, normalise Uzbek apostrophes, and truncate tokens to a stem prefix."""
    text = text.translate(_APOSTROPHES).lower()
    return [t.replace("'", "")[:STEM_LEN] for t in _TOKEN.findall(text)]


@dataclass(frozen=True)
class Chunk:
    source: str
    index: int
    heading: str
    text: str

    @property
    def ref(self) -> str:
        return f"{self.source}#{self.index}"


def split_into_chunks(source: str, text: str, max_chars: int = 1200) -> list[Chunk]:
    """Split ``text`` into chunks that never cross a Markdown heading."""
    chunks: list[Chunk] = []
    heading = ""
    buffer: list[str] = []
    size = 0

    def flush() -> None:
        nonlocal buffer, size
        body = "\n\n".join(buffer).strip()
        if body:
            chunks.append(Chunk(source, len(chunks), heading, body))
        buffer, size = [], 0

    for block in re.split(r"\n\s*\n", text):
        block = block.strip()
        if not block:
            continue
        if block.startswith("#"):
            flush()
            heading = block.splitlines()[0].lstrip("# ").strip()
            rest = "\n".join(block.splitlines()[1:]).strip()
            block = rest
            if not block:
                continue
        if size + len(block) > max_chars and buffer:
            flush()
        buffer.append(block)
        size += len(block)
    flush()
    return chunks


class KnowledgeBase:
    """BM25 index over a list of chunks."""

    def __init__(self, chunks: list[Chunk], k1: float = 1.5, b: float = 0.75) -> None:
        self.chunks = chunks
        self.k1 = k1
        self.b = b
        self._tf = [Counter(tokenize(f"{c.heading} {c.text}")) for c in chunks]
        self._len = [sum(tf.values()) for tf in self._tf]
        self._avg_len = (sum(self._len) / len(chunks)) if chunks else 0.0
        df: Counter[str] = Counter()
        for tf in self._tf:
            df.update(tf.keys())
        n = len(chunks)
        self._idf = {t: math.log(1 + (n - d + 0.5) / (d + 0.5)) for t, d in df.items()}

    @classmethod
    def from_directory(cls, path: str | Path, max_chars: int = 1200) -> KnowledgeBase:
        root = Path(path)
        if not root.is_dir():
            raise FileNotFoundError(f"Manba papkasi topilmadi: {root}")
        chunks: list[Chunk] = []
        for file in sorted(root.rglob("*")):
            if file.suffix.lower() in SUPPORTED_SUFFIXES and file.is_file():
                text = file.read_text(encoding="utf-8")
                name = file.relative_to(root).as_posix()
                chunks.extend(split_into_chunks(name, text, max_chars))
        return cls(chunks)

    def __len__(self) -> int:
        return len(self.chunks)

    def search(self, query: str, top_k: int = 4) -> list[tuple[Chunk, float]]:
        """Return up to ``top_k`` chunks with a positive score, best first."""
        terms = tokenize(query)
        if not terms or not self.chunks:
            return []
        scored: list[tuple[Chunk, float]] = []
        for chunk, tf, length in zip(self.chunks, self._tf, self._len):
            score = 0.0
            for term in set(terms):
                freq = tf.get(term, 0)
                if not freq:
                    continue
                norm = freq + self.k1 * (1 - self.b + self.b * length / (self._avg_len or 1))
                score += self._idf.get(term, 0.0) * freq * (self.k1 + 1) / norm
            if score > 0:
                scored.append((chunk, score))
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return scored[:top_k]
