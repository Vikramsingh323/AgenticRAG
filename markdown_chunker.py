#!/usr/bin/env python3
"""
Markdown chunking utilities with LLM-based strategy selection.

Features:
- LLM analysis to recommend chunking strategy (optional; falls back to heuristics if no API key)
- Header-based chunking (`MarkdownHeaderTextSplitter`)
- Semantic chunking using sentence-transformers embeddings and cosine similarity
- Merging semantically similar chunks (threshold configurable)
- Hybrid approach (header + semantic)
- Outputs JSON chunks with metadata to `doc_dump_chunks/`
- Logging, error handling and type hints throughout

Usage:
    from pathlib import Path
    from markdown_chunker import MarkdownChunker

    chunker = MarkdownChunker(threshold=0.8)
    chunker.process_markdown_file(Path('doc_dump_md/technical_guide.md'))

"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any

import numpy as np

# optional OpenAI usage; handle gracefully if not available
try:
    import openai
    _OPENAI_AVAILABLE = True
except Exception:
    _OPENAI_AVAILABLE = False

# sentence-transformers for embeddings
try:
    from sentence_transformers import SentenceTransformer
    _SENTENCE_TRANSFORMERS_AVAILABLE = True
except Exception:
    _SENTENCE_TRANSFORMERS_AVAILABLE = False


# ----------------------------- Logging -------------------------------------
logger = logging.getLogger("markdown_chunker")
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S"))
    logger.addHandler(ch)
logger.setLevel(logging.INFO)


# ----------------------------- Data models ---------------------------------

@dataclass
class Chunk:
    id: str
    text: str
    source: str
    strategy: str
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # embedding may be numpy array; ensure serializable
        if isinstance(d.get("embedding"), (list, tuple)):
            d["embedding"] = list(d["embedding"])
        elif hasattr(d.get("embedding"), "tolist"):
            d["embedding"] = d["embedding"].tolist()
        return d


# ----------------------------- Helpers -------------------------------------

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    try:
        if a is None or b is None:
            return 0.0
        denom = (np.linalg.norm(a) * np.linalg.norm(b))
        if denom == 0:
            return 0.0
        return float(np.dot(a, b) / denom)
    except Exception:
        return 0.0


# ----------------------------- Splitters -----------------------------------

class MarkdownHeaderTextSplitter:
    """Split markdown into chunks based on header hierarchy.

    Splits at any header line that begins with `#` and groups following
    content under that header. Top-level text before first header is also
    returned as a chunk (with header "_root_").
    """

    def split(self, text: str) -> List[Tuple[str, int, int, str]]:
        """
        Returns list of tuples: (header, start_line, end_line, chunk_text)
        start_line and end_line are 1-based line numbers within the input text.
        """
        lines = text.splitlines()
        chunks: List[Tuple[str, int, int, str]] = []

        current_header = "_root_"
        current_start = 1
        for i, line in enumerate(lines, start=1):
            if line.strip().startswith("#"):
                # close previous chunk
                if i - 1 >= current_start:
                    chunk_text = "\n".join(lines[current_start - 1: i - 1]).strip()
                    chunks.append((current_header, current_start, i - 1, chunk_text))
                # start new
                current_header = line.strip()
                current_start = i
        # final chunk
        if len(lines) >= current_start:
            chunk_text = "\n".join(lines[current_start - 1:]).strip()
            chunks.append((current_header, current_start, len(lines), chunk_text))

        # filter empty chunks
        filtered = [(h, s, e, t) for (h, s, e, t) in chunks if t.strip()]
        return filtered


# ----------------------------- Chunker ------------------------------------

class MarkdownChunker:
    """Main chunking utility supporting header, semantic and hybrid strategies.

    Parameters:
        threshold: cosine similarity threshold to merge chunks (default 0.8)
        model_name: sentence-transformers model name for embeddings
    """

    def __init__(self, threshold: float = 0.8, model_name: str = "all-MiniLM-L6-v2") -> None:
        self.threshold = threshold
        self.model_name = model_name
        self.header_splitter = MarkdownHeaderTextSplitter()

        if _SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.model = SentenceTransformer(self.model_name)
                logger.info(f"Loaded embedding model: {self.model_name}")
            except Exception as e:
                logger.warning(f"Failed to load sentence-transformers model: {e}")
                self.model = None
        else:
            logger.warning("sentence-transformers not installed; semantic methods will be disabled")
            self.model = None

    # -------------------- LLM-based strategy recommendation -----------------
    def analyze_with_llm(self, text: str) -> str:
        """Use an LLM to recommend chunking strategy for the provided markdown.

        Returns one of: 'header', 'semantic', 'hybrid'. Falls back to heuristic.
        """
        # If OpenAI is available and key configured, try it
        if _OPENAI_AVAILABLE and os.environ.get("OPENAI_API_KEY"):
            try:
                prompt = (
                    "You are a helper that recommends a markdown chunking strategy.\n"
                    "Given the following markdown content (first 2000 characters), reply with exactly one word: 'header', 'semantic', or 'hybrid'.\n\n"
                    f"Content:\n{text[:2000]}\n\nStrategy:"
                )
                resp = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0,
                    max_tokens=4,
                )
                choice = resp["choices"][0]["message"]["content"].strip().lower()
                if choice in {"header", "semantic", "hybrid"}:
                    logger.info(f"LLM recommended strategy: {choice}")
                    return choice
                logger.warning(f"LLM returned unexpected result: {choice}; falling back to heuristic")
            except Exception as e:
                logger.warning(f"LLM analysis failed: {e}; falling back to heuristic")

        # Heuristic fallback:
        # If many headers -> header; if long paragraphs with few headers -> semantic; else hybrid
        header_count = text.count("\n#") + text.count("\n##")
        avg_para_len = sum(len(p.split()) for p in text.split('\n\n') if p.strip()) / max(1, len([p for p in text.split('\n\n') if p.strip()]))
        logger.debug(f"Heuristic header_count={header_count}, avg_para_len={avg_para_len:.1f}")
        if header_count >= 3 and avg_para_len < 200:
            return "header"
        if header_count <= 1 and avg_para_len >= 100:
            return "semantic"
        return "hybrid"

    # -------------------- Header-based chunking ---------------------------
    def header_chunk(self, markdown_text: str, source: str) -> List[Chunk]:
        pieces = self.header_splitter.split(markdown_text)
        chunks: List[Chunk] = []
        for idx, (header, start, end, text) in enumerate(pieces, start=1):
            cid = f"{Path(source).stem}_hdr_{idx:03d}"
            chunks.append(Chunk(id=cid, text=text, source=source, strategy="header", start_line=start, end_line=end, metadata={"header": header}))
        logger.info(f"Header chunking produced {len(chunks)} chunk(s)")
        return chunks

    # -------------------- Semantic chunking & merging ---------------------
    def semantic_chunk(self, markdown_text: str, source: str) -> List[Chunk]:
        """Create initial sentence-based chunks and merge semantically similar ones.

        Steps:
         - Split text into paragraphs, then into sentences
         - Build initial chunks (paragraphs)
         - Compute embeddings and iteratively merge chunks with similarity >= threshold
        """
        if self.model is None:
            raise RuntimeError("Embedding model not available for semantic chunking")

        # very simple paragraph split
        paras = [p.strip() for p in markdown_text.split('\n\n') if p.strip()]
        initial_chunks: List[Chunk] = []
        for i, p in enumerate(paras, start=1):
            cid = f"{Path(source).stem}_sem_{i:03d}"
            initial_chunks.append(Chunk(id=cid, text=p, source=source, strategy="semantic", start_line=None, end_line=None, metadata={"para_index": i}))

        if not initial_chunks:
            return []

        texts = [c.text for c in initial_chunks]
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        except Exception as e:
            logger.error(f"Failed to compute embeddings: {e}")
            return initial_chunks

        # Attach embeddings
        for c, emb in zip(initial_chunks, embeddings):
            c.embedding = emb.tolist() if hasattr(emb, 'tolist') else emb

        # Greedy merging: if any two chunks have similarity >= threshold, merge them into earlier one
        merged = []  # List[Chunk]
        used = [False] * len(initial_chunks)

        for i, base in enumerate(initial_chunks):
            if used[i]:
                continue
            current_text = base.text
            current_emb = np.array(base.embedding, dtype=float)
            used[i] = True
            for j in range(i + 1, len(initial_chunks)):
                if used[j]:
                    continue
                sim = cosine_similarity(current_emb, np.array(initial_chunks[j].embedding, dtype=float))
                if sim >= self.threshold:
                    # merge
                    current_text = current_text + "\n\n" + initial_chunks[j].text
                    # update embedding as mean
                    other_emb = np.array(initial_chunks[j].embedding, dtype=float)
                    current_emb = (current_emb + other_emb) / 2.0
                    used[j] = True
            # finalize
            cid = f"{Path(source).stem}_sem_merged_{len(merged)+1:03d}"
            merged_chunk = Chunk(id=cid, text=current_text, source=source, strategy="semantic_merged", embedding=current_emb.tolist(), metadata={"merged_from": []})
            merged.append(merged_chunk)

        logger.info(f"Semantic chunking produced {len(merged)} merged chunk(s) from {len(initial_chunks)} initial paragraphs")
        return merged

    # -------------------- Hybrid (header + semantic) ---------------------
    def hybrid_chunk(self, markdown_text: str, source: str) -> List[Chunk]:
        header_chunks = self.header_chunk(markdown_text, source)
        result_chunks: List[Chunk] = []
        for h in header_chunks:
            # For each header chunk, apply semantic merging if it's long and model available
            text = h.text
            if self.model is not None and len(text.split()) > 60:
                try:
                    sem_chunks = self.semantic_chunk(text, source)
                    # tag with header in metadata
                    for sc in sem_chunks:
                        sc.metadata.setdefault('header', h.metadata.get('header'))
                        result_chunks.append(sc)
                except Exception as e:
                    logger.warning(f"Semantic within header failed: {e}; falling back to header chunk")
                    result_chunks.append(h)
            else:
                result_chunks.append(h)
        logger.info(f"Hybrid chunking produced total {len(result_chunks)} chunk(s)")
        return result_chunks

    # -------------------- Public API ------------------------------------
    def chunk_markdown(self, markdown_text: str, source: str, strategy: Optional[str] = None) -> List[Chunk]:
        """Chunk markdown according to a chosen strategy. If strategy is None,
        use LLM/heuristic recommendation."""
        try:
            chosen = strategy or self.analyze_with_llm(markdown_text)
        except Exception as e:
            logger.warning(f"Strategy analysis failed: {e}; defaulting to hybrid")
            chosen = "hybrid"

        logger.info(f"Using chunking strategy: {chosen}")
        if chosen == "header":
            return self.header_chunk(markdown_text, source)
        if chosen == "semantic":
            return self.semantic_chunk(markdown_text, source)
        # hybrid
        return self.hybrid_chunk(markdown_text, source)

    def save_chunks(self, chunks: List[Chunk], outdir: Path) -> List[Path]:
        outdir.mkdir(parents=True, exist_ok=True)
        paths: List[Path] = []
        for c in chunks:
            try:
                fname = f"{c.id}.json"
                dest = outdir / fname
                dest.write_text(json.dumps(c.to_dict(), ensure_ascii=False, indent=2), encoding='utf-8')
                paths.append(dest)
            except Exception as e:
                logger.error(f"Failed to save chunk {c.id}: {e}")
        logger.info(f"Saved {len(paths)} chunk JSON files to {outdir}")
        return paths

    def process_markdown_file(self, md_path: Path, outdir: Optional[Path] = None, strategy: Optional[str] = None) -> List[Path]:
        if outdir is None:
            outdir = Path("doc_dump_chunks")
        outdir = Path(outdir)
        try:
            text = md_path.read_text(encoding='utf-8')
        except Exception as e:
            logger.error(f"Unable to read markdown file {md_path}: {e}")
            return []

        try:
            chunks = self.chunk_markdown(text, str(md_path), strategy=strategy)
        except Exception as e:
            logger.error(f"Chunking failed for {md_path}: {e}")
            return []

        # Add global metadata
        for c in chunks:
            c.metadata = c.metadata or {}
            c.metadata.setdefault('source_file', str(md_path))
            c.metadata.setdefault('strategy', c.strategy)
            c.metadata.setdefault('threshold', self.threshold)

        saved = self.save_chunks(chunks, outdir)
        return saved

    def process_all_markdown_in_dir(self, md_dir: Path, outdir: Optional[Path] = None, strategy: Optional[str] = None) -> Dict[str, List[str]]:
        md_dir = Path(md_dir)
        files = sorted(md_dir.glob("*.md"))
        results: Dict[str, List[str]] = {}
        for md in files:
            try:
                saved = self.process_markdown_file(md, outdir=outdir, strategy=strategy)
                results[str(md)] = [str(p) for p in saved]
            except Exception as e:
                logger.error(f"Failed processing {md}: {e}")
                results[str(md)] = []
        return results


# ----------------------------- CLI runner ---------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Chunk markdown files with header/semantic/hybrid strategies")
    parser.add_argument("--input", "-i", default="doc_dump_md", help="Input markdown directory")
    parser.add_argument("--output", "-o", default="doc_dump_chunks", help="Output JSON chunks directory")
    parser.add_argument("--strategy", "-s", choices=["header", "semantic", "hybrid"], default=None, help="Chunking strategy (if omitted use LLM/heuristic)")
    parser.add_argument("--threshold", "-t", type=float, default=0.8, help="Semantic similarity threshold for merging (default 0.8)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    chunker = MarkdownChunker(threshold=args.threshold)
    out = chunker.process_all_markdown_in_dir(Path(args.input), outdir=Path(args.output), strategy=args.strategy)
    print(json.dumps(out, indent=2))
