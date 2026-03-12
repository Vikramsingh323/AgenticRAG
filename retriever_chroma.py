#!/usr/bin/env python3
"""Hybrid retriever using Chroma + sentence-transformers.

Features:
- Build a Retriever that performs semantic search via Chroma embeddings
- Combine semantic scores with keyword matching (hybrid search)
- Optional reranking via CrossEncoder when available
- Accepts chat history to enrich reranking context
- Upsert single chunk into Chroma collection

"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple

import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    from sentence_transformers.cross_encoder import CrossEncoder
except Exception:
    SentenceTransformer = None
    CrossEncoder = None

# BM25 keyword search support
try:
    from rank_bm25 import BM25Okapi
except Exception:
    BM25Okapi = None

try:
    import chromadb
except Exception:
    chromadb = None

logger = logging.getLogger("retriever_chroma")
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S"))
    logger.addHandler(ch)
logger.setLevel(logging.INFO)


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    if a is None or b is None:
        return 0.0
    try:
        a = np.array(a, dtype=float)
        b = np.array(b, dtype=float)
        na = np.linalg.norm(a)
        nb = np.linalg.norm(b)
        if na == 0 or nb == 0:
            return 0.0
        return float(np.dot(a, b) / (na * nb))
    except Exception:
        return 0.0


@dataclass
class Hit:
    id: str
    text: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]]
    sem_score: float
    keyword_score: float
    final_score: float


class Retriever:
    def __init__(self, persist_dir: Path | str = "chroma_store", collection_name: str = "doc_chunks", embed_model: str = "all-MiniLM-L6-v2", cross_encoder_model: Optional[str] = "cross-encoder/ms-marco-MiniLM-L-6-v2") -> None:
        if chromadb is None:
            raise RuntimeError("chromadb not installed")
        if SentenceTransformer is None:
            raise RuntimeError("sentence-transformers not installed")

        self.persist_dir = Path(persist_dir)
        self.collection_name = collection_name
        self.client = chromadb.PersistentClient(path=str(self.persist_dir))
        # get or create collection
        self.collection = self.client.get_or_create_collection(name=collection_name)

        self.embedder = SentenceTransformer(embed_model)
        logger.info(f"Loaded embedder: {embed_model}")

        # load all documents for BM25
        self.bm25 = None
        self._doc_texts: List[str] = []
        self._doc_ids: List[str] = []
        if BM25Okapi is not None:
            try:
                # fetch existing docs from collection
                all_data = self.collection.get(include=["ids","documents"])
                docs = all_data.get("documents", [])
                ids = all_data.get("ids", [])
                # flatten lists
                docs_flat = [d for sub in docs for d in sub]
                ids_flat = [i for sub in ids for i in sub]
                self._doc_texts = docs_flat
                self._doc_ids = ids_flat
                tokenized = [doc.lower().split() for doc in self._doc_texts]
                self.bm25 = BM25Okapi(tokenized)
                logger.info("Initialized BM25 index with %d documents", len(self._doc_texts))
            except Exception as e:
                logger.warning(f"Failed to build BM25 index: {e}")

        self.cross_encoder = None
        if CrossEncoder is not None and cross_encoder_model:
            try:
                self.cross_encoder = CrossEncoder(cross_encoder_model)
                logger.info(f"Loaded cross-encoder: {cross_encoder_model}")
            except Exception as e:
                logger.warning(f"Failed to load cross-encoder: {e}")

    def upsert_chunk(self, chunk: Dict[str, Any]) -> None:
        """Add or update a single chunk JSON object into the collection."""
        cid = chunk.get("id")
        text = chunk.get("text", "")
        metadata = {k: v for k, v in chunk.items() if k not in ("text", "embedding")}
        emb = chunk.get("embedding")
        if emb is None:
            emb = self.embedder.encode([text], convert_to_numpy=True)[0].tolist()
        # chroma's add will append; some versions support update/replace - use add which will dedup if ids same
        self.collection.add(ids=[cid], documents=[text], metadatas=[metadata], embeddings=[emb])
        # update BM25 in-memory index
        if BM25Okapi is not None:
            try:
                # append to texts and ids
                self._doc_texts.append(text)
                self._doc_ids.append(cid)
                tokenized = [doc.lower().split() for doc in self._doc_texts]
                self.bm25 = BM25Okapi(tokenized)
            except Exception as e:
                logger.warning(f"Failed to update BM25 index on upsert: {e}")

    def _semantic_candidates(self, query: str, top_k: int = 10, fetch_k: Optional[int] = None) -> List[Hit]:
        fetch_k = fetch_k or max(50, top_k * 5)
        q_emb = self.embedder.encode([query], convert_to_numpy=True)[0]
        result = self.collection.query(query_embeddings=[q_emb.tolist()], n_results=fetch_k, include=["metadatas", "documents", "embeddings"])  # type: ignore[arg-type]
        docs = result.get("documents", [[]])[0]
        ids = result.get("ids", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        embeddings = result.get("embeddings", [[]])[0]

        hits: List[Hit] = []
        for i, doc in enumerate(docs):
            emb = np.array(embeddings[i], dtype=float) if (embeddings is not None and len(embeddings) > i) else None
            sem = _cosine(np.array(q_emb, dtype=float), emb) if emb is not None else 0.0
            hits.append(Hit(id=ids[i], text=doc, metadata=metadatas[i] if (metadatas is not None and i < len(metadatas)) else {}, embedding=emb.tolist() if emb is not None else None, sem_score=sem, keyword_score=0.0, final_score=sem))
        return hits

    def _bm25_scores(self, query: str) -> Dict[str, float]:
        """Return BM25 scores for each doc id (normalized 0..1)."""
        if self.bm25 is None:
            return {}
        tokenized_q = query.lower().split()
        scores = self.bm25.get_scores(tokenized_q)
        if not scores.any():
            return {}
        # normalize
        max_score = float(scores.max())
        if max_score <= 0:
            return {}
        normalized = scores / max_score
        return {self._doc_ids[i]: float(normalized[i]) for i in range(len(self._doc_ids))}

    def search(self, query: str, top_k: int = 10, keywords: Optional[List[str]] = None, hybrid_weight: float = 0.7, rerank: bool = True, chat_history: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Hybrid search combining semantic and keyword signals.

        - `keywords`: list of important tokens/phrases to boost
        - `hybrid_weight`: weight for semantic vs keyword (0..1)
        - `rerank`: if True and cross-encoder available, rerank top candidates with cross-encoder
        - `chat_history`: optional list of previous messages (strings) to include when reranking
        """
        candidates = self._semantic_candidates(query, top_k=top_k)

        # compute keyword scores using either explicit keywords or BM25
        kw_scores = {}
        if keywords:
            kws = [k.lower() for k in keywords]
            for c in candidates:
                text = (c.text or "").lower()
                score = 0.0
                for kw in kws:
                    if kw in text:
                        score += 1.0
                c.keyword_score = score / max(1.0, len(kws))
        else:
            # default to BM25 scores if available
            bm = self._bm25_scores(query)
            for c in candidates:
                c.keyword_score = bm.get(c.id, 0.0)

        # normalize semantic scores into 0..1
        sems = np.array([c.sem_score for c in candidates], dtype=float)
        if sems.max() > 0:
            sems = (sems - sems.min()) / (sems.max() - sems.min() + 1e-12)
        else:
            sems = np.zeros_like(sems)
        for i, c in enumerate(candidates):
            c.sem_score = float(sems[i])

        # combine
        for c in candidates:
            c.final_score = hybrid_weight * c.sem_score + (1.0 - hybrid_weight) * c.keyword_score

        # keep top N for potential rerank
        candidates = sorted(candidates, key=lambda h: h.final_score, reverse=True)[: max(top_k * 3, top_k)]

        # optional reranking with cross-encoder
        if rerank and self.cross_encoder is not None:
            pairs = []
            ctx_prefix = ""
            if chat_history:
                ctx_prefix = "\n".join(chat_history[-5:]) + "\n"
            for c in candidates:
                pairs.append((ctx_prefix + query, c.text))
            try:
                scores = self.cross_encoder.predict(pairs)
                # normalize cross scores
                arr = np.array(scores, dtype=float)
                if arr.max() > arr.min():
                    arr = (arr - arr.min()) / (arr.max() - arr.min())
                for i, c in enumerate(candidates):
                    # blend cross-encoder score with previous final_score
                    c.final_score = 0.6 * float(arr[i]) + 0.4 * c.final_score
            except Exception as e:
                logger.warning(f"Cross-encoder rerank failed: {e}")

        # return top_k
        candidates = sorted(candidates, key=lambda h: h.final_score, reverse=True)[:top_k]

        return [
            {
                "id": c.id,
                "text": c.text,
                "metadata": c.metadata,
                "score": c.final_score,
                "sem_score": c.sem_score,
                "keyword_score": c.keyword_score,
            }
            for c in candidates
        ]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Retriever smoke test")
    parser.add_argument("--persist", "-p", default="chroma_store")
    parser.add_argument("--collection", "-c", default="doc_chunks")
    parser.add_argument("--query", "-q", default="performance optimizations for database")
    args = parser.parse_args()

    r = Retriever(persist_dir=Path(args.persist), collection_name=args.collection)
    res = r.search(args.query, top_k=5, keywords=None, rerank=True, chat_history=None)
    for i, rj in enumerate(res, start=1):
        print(i, rj.get("id"), f"score={rj.get('score'):.3f}")
