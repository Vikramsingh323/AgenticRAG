#!/usr/bin/env python3
"""
Integration demo: Chunking → Vectorstore → Retriever → RAG Agent pipeline.

This script orchestrates the full end-to-end flow:
1. Chunk markdown files from `doc_dump_md/`
2. Build Chroma vectorstore from chunks
3. Create retriever
4. Run RAG agent on sample questions
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger("integration_demo")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("[%(asctime)s] %(name)s %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S"))
    logger.addHandler(ch)


def main() -> None:
    md_dir = Path("doc_dump_md")
    chunk_dir = Path("doc_dump_chunks")
    persist_dir = Path("chroma_store")

    # Step 1: Chunk markdown files
    logger.info("=" * 80)
    logger.info("STEP 1: Chunk markdown files")
    logger.info("=" * 80)

    if chunk_dir.exists():
        chunk_files = list(chunk_dir.glob("*.json"))
        logger.info(f"Found {len(chunk_files)} existing chunks in {chunk_dir}")
    else:
        logger.info(f"Chunking markdown files from {md_dir}...")
        from markdown_chunker import MarkdownChunker

        chunker = MarkdownChunker(threshold=0.8)
        result = chunker.process_all_markdown_in_dir(md_dir, outdir=chunk_dir, strategy=None)
        total_chunks = sum(len(v) for v in result.values())
        logger.info(f"Created {total_chunks} chunks across {len(result)} files")
        for src, dst_list in result.items():
            logger.info(f"  {src}: {len(dst_list)} chunks")

    # Step 2: Build Chroma vectorstore
    logger.info("\n" + "=" * 80)
    logger.info("STEP 2: Build Chroma vectorstore from chunks")
    logger.info("=" * 80)

    from vectorstore_chroma import create_chroma_from_chunks

    summary = create_chroma_from_chunks(chunk_dir, persist_dir)
    logger.info(f"Vectorstore created with {summary.get('added')} chunks")

    # Step 3: Create retriever
    logger.info("\n" + "=" * 80)
    logger.info("STEP 3: Initialize retriever")
    logger.info("=" * 80)

    from retriever_chroma import Retriever

    retriever = Retriever(persist_dir=persist_dir, collection_name="doc_chunks")
    logger.info("Retriever initialized and ready")

    # Step 4: Create RAG agent
    logger.info("\n" + "=" * 80)
    logger.info("STEP 4: Initialize RAG agent")
    logger.info("=" * 80)

    from rag_agent import RAGAgent

    agent = RAGAgent(
        retriever=retriever,
        k=10,
        num_answers=5,
        scoring_weights={"relevance": 0.4, "coherence": 0.3, "coverage": 0.3},
        max_workers=4,
    )
    logger.info("RAG agent initialized")

    # Step 5: Run sample queries
    logger.info("\n" + "=" * 80)
    logger.info("STEP 5: Run sample queries")
    logger.info("=" * 80)

    sample_questions = [
        "What are the main features described in the documents?",
        "How should I use this system?",
        "What are the key recommendations?",
    ]

    results = []
    for i, q in enumerate(sample_questions, start=1):
        logger.info(f"\nQuery {i}/{len(sample_questions)}: {q}")
        try:
            result = agent.process(q, chat_history=None)
            results.append({
                "question": q,
                "answer": result.answer_text[:200] + "...",
                "confidence": result.confidence_score,
                "chunk_count": len(result.source_chunk_ids),
            })
            logger.info(f"✓ Answer generated (confidence={result.confidence_score:.3f})")
        except Exception as e:
            logger.error(f"✗ Failed to process query: {e}")

    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("INTEGRATION TEST SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Processed {len(results)} queries successfully")
    for r in results:
        logger.info(f"  Q: {r['question'][:60]}...")
        logger.info(f"     Confidence: {r['confidence']:.3f}, Chunks: {r['chunk_count']}")

    logger.info(f"\nAgent logs saved to: {Path('agent_logs').absolute()}")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
