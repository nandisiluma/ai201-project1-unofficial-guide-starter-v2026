"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`split_documents` below is deliberately plain. It cuts every document into
fixed-size pieces with a fixed overlap and pays no attention to where sentences
or paragraphs end. It works, and it is not good.

On a corpus of short posts it may not cut anything at all: `campus_life` comes
out as 88 documents and 88 chunks, because almost nothing in it reaches 800
characters. That is the baseline, not a bug — Milestone 3 is where you decide
whether one post should stay one chunk.

Your job in Milestone 3 is to replace the *body* of `split_documents` with a
strategy that fits the documents you actually read in Milestone 1. Keep the
name and the shape of what it returns — the rest of the pipeline calls it, and
your README has to name the function that produced your chunks.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch back
to it, write down what you saw, and move on. That's a real observation about
your pipeline, not giving up.
"""

import re
from dataclasses import dataclass

import config
from ingest import Document

# A sentence boundary: end punctuation followed by whitespace and the start
# of the next sentence. Only used as a fallback for a paragraph too long to
# fit in one chunk on its own — see split_documents.
_SENTENCE_BOUNDARY = re.compile(r'(?<=[.!?])\s+(?=[A-Z0-9"\'#])')


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    Split documents into chunks. ⚠️ REPLACE THE BODY OF THIS IN MILESTONE 3.

    Right now it just calls the fallback. That is the plain, generic behaviour
    the brief is talking about.

    When you write your own strategy, set `produced_by` to
    "chunker.py::split_documents" so your README's Sample Chunks section names
    the right function. `app.py chunks` prints that string for you.

    Things worth thinking about before you write any code:
      - Are your documents short posts or long guides?
      - Is the useful information in one sentence, or spread over a paragraph?
      - Would splitting on paragraph breaks keep more thoughts intact than
        splitting on a character count?
    """
    chunk_size = config.CHUNK_SIZE
    overlap = config.CHUNK_OVERLAP

    chunks: list[Chunk] = []
    for doc in documents:
        units: list[str] = []
        for paragraph in _split_paragraphs(doc.text):
            if len(paragraph) <= chunk_size:
                units.append(paragraph)
            else:
                # A single paragraph too long to be its own chunk. Split it
                # on sentence boundaries instead of falling back to a raw
                # character cut.
                units.extend(_split_sentences(paragraph))

        for index, piece in enumerate(_pack(units, chunk_size, overlap)):
            chunks.append(
                Chunk(
                    text=piece,
                    source=doc.source,
                    index=index,
                    produced_by="chunker.py::split_documents",
                )
            )

    return chunks


def _split_paragraphs(text: str) -> list[str]:
    """Break a document on blank lines — the section/paragraph breaks that
    already exist in these markdown guides, and that never fall mid-sentence."""
    return [p.strip() for p in text.split("\n\n") if p.strip()]


def _split_sentences(paragraph: str) -> list[str]:
    """Break one paragraph into sentences. Only called on a paragraph that
    doesn't fit in a chunk by itself."""
    return [s.strip() for s in _SENTENCE_BOUNDARY.split(paragraph) if s.strip()]


def _pack(units: list[str], chunk_size: int, overlap: int) -> list[str]:
    """
    Greedily pack whole units (paragraphs, or sentences from an oversized
    paragraph) into chunks up to chunk_size.

    When a chunk fills up, the last unit that was in it carries over into the
    front of the next chunk — that's the overlap, and because it's a whole
    unit rather than a character slice, it can't start mid-word either.
    """
    pieces: list[str] = []
    current: list[str] = []

    def length(units: list[str]) -> int:
        return sum(len(u) for u in units) + 2 * max(len(units) - 1, 0)

    for unit in units:
        if current and length(current + [unit]) > chunk_size:
            pieces.append("\n\n".join(current))
            carry = current[-1]
            current = [carry] if len(carry) <= overlap else []
        current.append(unit)

    if current:
        pieces.append("\n\n".join(current))

    return pieces


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
