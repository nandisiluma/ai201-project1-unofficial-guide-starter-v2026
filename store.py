"""
Stages 3 and 4 of the pipeline: embedding chunks and retrieving them.

Three things in here are worth knowing about, because they'd quietly break the
rest of the project if they were wrong:

1. The Chroma collection is created with cosine distance, explicitly. Chroma
   defaults to squared L2, and the 0.6 threshold the course uses is calibrated
   against cosine. Getting this wrong makes every distance number meaningless.

2. `search` returns the distance alongside each chunk. Milestone 4 has you
   compare distances, so they have to be visible.

3. The embedding model is the one Chroma bundles, not one loaded through
   `sentence-transformers`. It is the same model — `all-MiniLM-L6-v2`, 384
   dimensions — but it arrives as an ONNX build from Chroma's own CDN, so the
   install needs neither PyTorch nor a reachable Hugging Face. See `_embedder`.
"""

import os
import re
import shutil
from dataclasses import dataclass

# Must be set BEFORE chromadb is imported. Without it, some Chroma versions
# print "Failed to send telemetry event ..." on every single call — which looks
# exactly like a real error, isn't one, and cost a previous cohort a lot of
# confused help-channel messages.
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

import chromadb  # noqa: E402

import config
from chunker import Chunk


@dataclass
class Result:
    """One retrieved chunk and how far it was from the question."""

    text: str
    source: str
    label: str
    distance: float   # LOWER IS BETTER. 0.3 is close, 0.9 is unrelated.
    produced_by: str


_model = None

# The model Chroma bundles. Anything else in config.EMBEDDING_MODEL means
# "fetch that one from Hugging Face instead" — see `_embedder`.
BUNDLED_MODEL = "all-MiniLM-L6-v2"


class _OnnxEmbedder:
    """
    Chroma's built-in embedder, wrapped to look like the other two.

    Chroma's embedding functions are called directly and hand back numpy
    arrays. The rest of this file wants `.encode(texts)`, so the adapter lives
    here rather than making every caller care which embedder it got.
    """

    def __init__(self):
        from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

        # Force the CPU execution provider. Left to pick automatically, onnxruntime
        # prefers CoreML on macOS, and CoreML does not run this model correctly on
        # every Mac — it fails with an opaque "Non-zero status code" error instead
        # of falling back. CPU is slower per call but this model is small enough
        # that it doesn't matter, and it works everywhere.
        self._ef = ONNXMiniLM_L6_V2(preferred_providers=["CPUExecutionProvider"])

    def encode(self, texts, show_progress_bar: bool = False):
        return [vector.tolist() for vector in self._ef(list(texts))]


def _sentence_transformer(name: str):
    """
    The escape hatch: any model that isn't the bundled one.

    Unit 2's "try a second embedding model" stretch option comes through here,
    and so does anything you set `EMBEDDING_MODEL` to. This path *does* need
    `sentence-transformers` and a reachable Hugging Face, neither of which the
    default install has — which is the whole point of the default install.
    """
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise RuntimeError(
            f"config.EMBEDDING_MODEL is set to {name!r}, which isn't the model "
            f"Chroma bundles ({BUNDLED_MODEL!r}), so it has to be downloaded "
            f"from Hugging Face.\n"
            f"Install the optional dependency first:\n"
            f"    pip install 'sentence-transformers>=3.4,<3.5'\n"
            f"Or set EMBEDDING_MODEL back to {BUNDLED_MODEL!r}."
        ) from exc

    return SentenceTransformer(name)


def _embedder():
    """
    Load the embedding model once and keep it.

    First call is slow — it downloads about 80 MB. That's why setup happens
    before class.
    """
    global _model

    if _model is not None:
        return _model

    # Used only by this repo's own smoke test, which runs where no model can be
    # downloaded at all. Never set this yourself.
    if os.getenv("AI201_FAKE_EMBEDDINGS") == "1":
        from _smoke_embedder import FakeEmbedder

        _model = FakeEmbedder()
    elif config.EMBEDDING_MODEL == BUNDLED_MODEL:
        _model = _OnnxEmbedder()
    else:
        _model = _sentence_transformer(config.EMBEDDING_MODEL)

    return _model


def embed(texts: list[str]) -> list[list[float]]:
    """Turn text into vectors. Runs on your machine, costs no API quota."""
    vectors = _embedder().encode(texts, show_progress_bar=False)
    # sentence-transformers and the smoke stand-in return something with a
    # .tolist(); _OnnxEmbedder has already done that conversion itself.
    return vectors.tolist() if hasattr(vectors, "tolist") else vectors


_TOKEN = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return _TOKEN.findall(text.lower())


_bm25_cache: dict[str, tuple] = {}


def _bm25_for(name: str, collection):
    """
    Build (and cache) a BM25 index over every chunk in a collection.

    Exact-keyword scoring, as a second signal alongside cosine distance. This
    corpus's towns are proper nouns — "Marchwood" either is or isn't in a
    chunk's text — and that's exactly the kind of exact match embeddings can
    bury under a chunk that's merely topically similar. BM25 rewards the
    literal match no matter how it scores on meaning.
    """
    cached = _bm25_cache.get(name)
    if cached is not None and cached[0] == collection.count():
        return cached[1:]

    from rank_bm25 import BM25Okapi

    raw = collection.get()
    ids = raw["ids"]
    texts = raw["documents"]
    metadatas = raw["metadatas"]
    bm25 = BM25Okapi([_tokenize(t) for t in texts])

    _bm25_cache[name] = (collection.count(), bm25, ids, texts, metadatas)
    return bm25, ids, texts, metadatas


def _hybrid_search(question: str, top_k: int, collection) -> list[Result]:
    """
    Combine semantic (cosine) and keyword (BM25) rankings with Reciprocal
    Rank Fusion, instead of ranking on meaning alone.

    Why: a question naming several towns by name can have a generic
    thematic document (about walking, or transport, region-wide) rank
    closer in *meaning* than any one town's own guide, because the generic
    doc's entire content is that topic while the town's guide only mentions
    it in passing. With a fixed top_k, that crowds out the specific towns
    the question is actually asking about — raising top_k just pulls in
    more generic chunks, not the missing towns (measured directly: on this
    corpus, Marchwood's own relevant chunk doesn't rank above position 15).
    BM25 fixes this because it scores the literal token "Marchwood",
    independent of how the rest of the chunk reads on topic.

    RRF (rank, not raw score) is used because cosine distance and BM25
    score live on unrelated, incomparable scales — fusing by rank avoids
    having to invent a weighting between them.
    """
    n = collection.count()

    semantic = collection.query(query_embeddings=embed([question]), n_results=n)
    sem_ids = semantic["ids"][0]
    sem_docs = semantic["documents"][0]
    sem_metas = semantic["metadatas"][0]
    sem_distances = semantic["distances"][0]
    semantic_rank = {doc_id: rank for rank, doc_id in enumerate(sem_ids, start=1)}
    distance_by_id = dict(zip(sem_ids, sem_distances))

    bm25, bm25_ids, _, _ = _bm25_for(collection.name, collection)
    scores = bm25.get_scores(_tokenize(question))
    bm25_order = sorted(range(len(bm25_ids)), key=lambda i: scores[i], reverse=True)
    bm25_rank = {bm25_ids[i]: rank for rank, i in enumerate(bm25_order, start=1)}

    k = 60  # standard RRF constant — de-emphasizes rank differences far down the list
    fused = sorted(
        sem_ids,
        key=lambda doc_id: 1 / (k + semantic_rank[doc_id]) + 1 / (k + bm25_rank.get(doc_id, len(sem_ids))),
        reverse=True,
    )

    doc_by_id = dict(zip(sem_ids, sem_docs))
    meta_by_id = dict(zip(sem_ids, sem_metas))

    results: list[Result] = []
    for doc_id in fused[:top_k]:
        meta = meta_by_id[doc_id]
        results.append(
            Result(
                text=doc_by_id[doc_id],
                source=str(meta.get("source", "unknown")),
                label=f"{meta.get('source', 'unknown')}#{meta.get('index', 0)}",
                # The ORIGINAL cosine distance, not a fused score — gate.py's
                # threshold is calibrated against cosine distance, and that
                # calibration has to keep meaning whatever ranking chose this
                # chunk.
                distance=float(distance_by_id[doc_id]),
                produced_by=str(meta.get("produced_by", "unknown")),
            )
        )
    return results


def _client():
    return chromadb.PersistentClient(
        path=str(config.CHROMA_DIR),
        settings=chromadb.config.Settings(anonymized_telemetry=False),
    )


def build_index(
    chunks: list[Chunk],
    corpus: str | None = None,
    variant: str = "default",
) -> int:
    """
    Embed every chunk and store it.

    `variant` lets you keep more than one index of the same corpus at the same
    time. In unit 2, when you compare two chunking strategies, index the second
    one as variant="v2" and you can query both instead of deleting the first
    and starting over.
    """
    name = config.collection_name(corpus, variant)
    client = _client()

    try:
        client.delete_collection(name)
    except Exception:
        pass

    collection = client.create_collection(
        name=name,
        # ⚠️ Do not remove. Chroma defaults to squared L2, and every distance
        # number in this course assumes cosine.
        metadata={"hnsw:space": "cosine"},
    )

    batch = 256
    for start in range(0, len(chunks), batch):
        window = chunks[start : start + batch]
        collection.add(
            ids=[f"{c.source}#{c.index}" for c in window],
            documents=[c.text for c in window],
            embeddings=embed([c.text for c in window]),
            metadatas=[
                {"source": c.source, "index": c.index, "produced_by": c.produced_by}
                for c in window
            ],
        )

    return len(chunks)


def search(
    question: str,
    top_k: int | None = None,
    corpus: str | None = None,
    variant: str = "default",
    hybrid: bool | None = None,
) -> list[Result]:
    """
    Retrieve the chunks closest in meaning to a question.

    Returns them nearest-first, each with its distance.

    `hybrid=True` adds a BM25 keyword pass alongside the semantic one and
    fuses the two rankings (see `_hybrid_search`) — see config.HYBRID_SEARCH
    for why this exists. Defaults to that config value.
    """
    top_k = top_k or config.TOP_K
    hybrid = config.HYBRID_SEARCH if hybrid is None else hybrid
    name = config.collection_name(corpus, variant)

    try:
        collection = _client().get_collection(name)
    except Exception as exc:
        raise RuntimeError(
            f"No index called '{name}'. Run `python app.py index` first."
        ) from exc

    if collection.count() == 0:
        raise RuntimeError(
            f"Index '{name}' exists but is empty. `python app.py index` must have "
            f"failed partway through. Run it again."
        )

    if hybrid:
        return _hybrid_search(question, top_k, collection)

    raw = collection.query(
        query_embeddings=embed([question]),
        n_results=min(top_k, collection.count()),
    )

    results: list[Result] = []
    for text, meta, distance in zip(
        raw["documents"][0], raw["metadatas"][0], raw["distances"][0]
    ):
        results.append(
            Result(
                text=text,
                source=str(meta.get("source", "unknown")),
                label=f"{meta.get('source', 'unknown')}#{meta.get('index', 0)}",
                distance=float(distance),
                produced_by=str(meta.get("produced_by", "unknown")),
            )
        )
    return results


def index_exists(corpus: str | None = None, variant: str = "default") -> bool:
    """Is there an index here to search, without searching it?

    `serve.py`'s health check asks this. It deliberately does not embed
    anything: loading the embedding model takes 80 MB and a few seconds, and a
    health check that heavy is a health check nobody can afford to call.
    """
    try:
        collection = _client().get_collection(config.collection_name(corpus, variant))
        return collection.count() > 0
    except Exception:
        return False


def reset():
    """Delete every index. Occasionally the fastest way out of a mess."""
    if config.CHROMA_DIR.exists():
        shutil.rmtree(config.CHROMA_DIR)
