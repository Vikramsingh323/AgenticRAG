#!/usr/bin/env python3
"""Create a Chroma vectorstore from chunk JSON files.

Functions:
 - create_chroma_from_chunks(chunk_dir, persist_dir, collection_name, ...)

This module computes embeddings using `sentence-transformers` and stores
them in a Chroma collection (local persistent directory).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any

import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except Exception:  # pragma: no cover - handled at runtime
    SentenceTransformer = None

try:
    import chromadb
except Exception:
    chromadb = None

logger = logging.getLogger("vectorstore_chroma")
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S"))
    logger.addHandler(ch)
logger.setLevel(logging.INFO)


def _load_chunk_jsons(chunk_dir: Path) -> List[Dict]:
    chunk_dir = Path(chunk_dir)
    files = sorted(chunk_dir.glob("*.json"))
    items: List[Dict] = []
    for p in files:
        try:
            obj = json.loads(p.read_text(encoding="utf-8"))
            items.append(obj)
        except Exception as e:
            logger.warning(f"Skipping invalid JSON {p}: {e}")
    logger.info(f"Loaded {len(items)} chunk(s) from {chunk_dir}")
    return items


def create_chroma_from_chunks(
    chunk_dir: Path,
    persist_dir: Path,
    collection_name: str = "doc_chunks",
    embedding_model_name: str = "all-MiniLM-L6-v2",
    batch_size: int = 64,
) -> Dict[str, int]:
    """Create or replace a Chroma collection from chunk JSONs.

    Args:
        chunk_dir: directory with chunk JSON files.
        persist_dir: directory where Chroma will persist data.
        collection_name: name of the Chroma collection to create/use.
        embedding_model_name: sentence-transformers model to compute embeddings.
        batch_size: number of texts to encode per batch.

    Returns:
        Summary dict with counts.
    """
    chunk_dir = Path(chunk_dir)
    persist_dir = Path(persist_dir)

    if chromadb is None:
        raise RuntimeError("chromadb is not installed. Please install chromadb in the environment.")

    items = _load_chunk_jsons(chunk_dir)
    if not items:
        logger.warning("No chunk JSON files found; nothing to add to Chroma.")
        return {"added": 0}

    texts = [it.get("text", "") for it in items]
    ids = [it.get("id") or f"chunk_{i:06d}" for i, it in enumerate(items, start=1)]
    # flatten nested metadata: Chroma doesn't allow dicts or None values in metadata
    metadatas: List[Dict[str, Any]] = []
    for it in items:
        meta = {}
        for k, v in it.items():
            if k not in ("text", "embedding", "metadata") and v is not None:
                if isinstance(v, (str, int, float, bool)):
                    meta[k] = v
                elif isinstance(v, dict):
                    for k2, v2 in v.items():
                        if isinstance(v2, (str, int, float, bool)) and v2 is not None:
                            meta[f"{k}_{k2}"] = v2
                elif isinstance(v, (list, tuple)):
                    meta[k] = str(v)
                else:
                    meta[k] = str(v)
        metadatas.append(meta)

    # load model
    model = SentenceTransformer(embedding_model_name)

    # compute embeddings in batches
    embeddings: List[List[float]] = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        emb = model.encode(batch, convert_to_numpy=True, show_progress_bar=False)
        # ensure list of lists
        for e in emb:
            embeddings.append(e.tolist() if hasattr(e, "tolist") else list(e))

    # init chroma client (new API)
    persist_dir.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(persist_dir))

    # create or get collection
    try:
        # if collection exists, delete it to replace
        existing_colls = [c.name for c in client.list_collections()]
        if collection_name in existing_colls:
            logger.info(f"Replacing existing collection: {collection_name}")
            client.delete_collection(name=collection_name)
    except Exception as e:
        logger.debug(f"Could not list existing collections: {e}")
        pass

    collection = client.get_or_create_collection(name=collection_name)

    # add documents
    collection.add(ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings)

    # persistence happens automatically in PersistentClient

    logger.info(f"Added {len(ids)} items to Chroma collection '{collection_name}' at {persist_dir}")
    return {"added": len(ids)}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Build Chroma vectorstore from chunk JSONs")
    parser.add_argument("--chunks", "-i", default="doc_dump_chunks", help="Directory with chunk JSON files")
    parser.add_argument("--persist", "-p", default="chroma_store", help="Chroma persist directory")
    parser.add_argument("--collection", "-c", default="doc_chunks", help="Chroma collection name")
    parser.add_argument("--model", "-m", default="all-MiniLM-L6-v2", help="sentence-transformers model name")
    args = parser.parse_args()

    summary = create_chroma_from_chunks(Path(args.chunks), Path(args.persist), collection_name=args.collection, embedding_model_name=args.model)
    print(summary)
