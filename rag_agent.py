#!/usr/bin/env python3
"""
RAG Agent: Retrieval-Augmented Generation with multi-answer synthesis and chunk scoring.

Pipeline:
1. Entity extraction from user question
2. Retrieve top K relevant chunks
3. Generate 5 independent answer sets in parallel
4. Score answers and chunks
5. Select top chunks based on combined scores
6. Augment context and generate final answer
7. Return with attribution and confidence
8. Log all intermediate steps

Configurable parameters:
- K: number of chunks to retrieve
- num_answers: number of independent answer sets (default 5)
- scoring_weights: dict with 'relevance', 'coherence', 'coverage' weights
"""

from __future__ import annotations

import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None

try:
    import openai
    _OPENAI_AVAILABLE = True
except Exception:
    _OPENAI_AVAILABLE = False

# ----------------------------- Setup & Logging --------------------------------

AGENT_LOG_DIR = Path("agent_logs")
AGENT_LOG_DIR.mkdir(exist_ok=True)

logger = logging.getLogger("rag_agent")
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S"))
    logger.addHandler(ch)
    # also log to file
    lf = logging.FileHandler(AGENT_LOG_DIR / f"agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    lf.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S"))
    logger.addHandler(lf)
logger.setLevel(logging.DEBUG)


# ----------------------------- Data Models ------------------------------------

@dataclass
class Entity:
    text: str
    type: str  # e.g., "NOUN", "VERB", "ENTITY", "CONCEPT"
    confidence: float


@dataclass
class ScoredAnswer:
    text: str
    relevance_score: float
    coherence_score: float
    coverage_score: float
    combined_score: float
    source_chunk_ids: List[str]


@dataclass
class ScoredChunk:
    id: str
    text: str
    relevance_to_question: float
    avg_relevance_to_answers: float
    combined_score: float
    used_in_answers: int  # how many of the 5 answers used this chunk


@dataclass
class FinalAnswer:
    answer_text: str
    confidence_score: float
    top_chunks: List[Dict[str, Any]]
    original_question: str
    source_chunk_ids: List[str]


# ----------------------------- Entity Extractor --------------------------------

class EntityExtractor:
    """Extract entities and intent from user questions."""

    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2") -> None:
        if SentenceTransformer is None:
            self.embedder = None
        else:
            self.embedder = SentenceTransformer(embedding_model)

    def extract_entities(self, question: str) -> List[Entity]:
        """Extract key entities from question using simple heuristics + embedding-based filtering."""
        entities: List[Entity] = []

        # simple heuristic: split on spaces, filter by length and commonality
        words = question.lower().split()
        stopwords = {"the", "a", "an", "is", "are", "was", "were", "be", "been", "being", "what", "how", "where", "when", "why", "which", "who", "do", "does", "did", "for", "to", "of", "in", "on", "at", "and", "or", "but", "can", "could", "would", "should", "will", "have", "has", "had"}

        candidates = [w for w in words if len(w) > 3 and w not in stopwords]

        # rank by TF-IDF-like heuristic (frequency in question)
        word_freq = {}
        for c in candidates:
            word_freq[c] = word_freq.get(c, 0) + 1
        sorted_cands = sorted(word_freq.items(), key=lambda x: -x[1])[:5]

        for word, freq in sorted_cands:
            conf = min(1.0, freq * 0.3)
            entities.append(Entity(text=word, type="KEYWORD", confidence=conf))

        logger.debug(f"Extracted {len(entities)} entities from question: {[e.text for e in entities]}")
        return entities

    def compute_question_embedding(self, question: str) -> np.ndarray:
        """Get embedding for question."""
        if self.embedder is None:
            return np.zeros(384)
        emb = self.embedder.encode([question], convert_to_numpy=True)[0]
        return emb


# ----------------------------- Answer Generator --------------------------------

class AnswerGenerator:
    """Generate candidate answers from chunk combinations."""

    def __init__(self, model: str = "gpt-4o-mini") -> None:
        self.model = model
        self.openai_available = _OPENAI_AVAILABLE and os.environ.get("OPENAI_API_KEY")

    def generate_answer(self, question: str, chunks: List[Dict[str, Any]]) -> str:
        """Generate an answer using provided chunks."""
        if not chunks:
            if self.openai_available:
                try:
                    resp = openai.ChatCompletion.create(
                        model=self.model,
                        messages=[{"role": "user", "content": question}],
                        temperature=0.7,
                        max_tokens=300,
                    )
                    return resp["choices"][0]["message"]["content"]
                except Exception as e:
                    logger.warning(f"OpenAI generation failed: {e}")
            return f"Unable to generate answer for: {question}"

        context = "\n\n".join([f"[{c.get('id')}] {c.get('text', '')}" for c in chunks])
        prompt = f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer (concise, 150 words max):"

        if self.openai_available:
            try:
                resp = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=300,
                )
                return resp["choices"][0]["message"]["content"]
            except Exception as e:
                logger.warning(f"OpenAI generation failed: {e}")

        # fallback: mock answer from chunks
        return f"Based on the provided context about {', '.join([c.get('id') for c in chunks][:2])}: Unable to generate (OpenAI not available)."


# ----------------------------- Scoring ----------------------------------------

class ChunkScorer:
    """Score chunks and answers."""

    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2") -> None:
        if SentenceTransformer is None:
            raise RuntimeError("sentence-transformers required for ChunkScorer")
        self.embedder = SentenceTransformer(embedding_model)

    def score_answer_relevance(self, question: str, answer: str, chunks: List[Dict[str, Any]]) -> float:
        """Score answer relevance to question (0-1)."""
        if not answer or len(answer) < 10:
            return 0.0
        q_emb = self.embedder.encode([question], convert_to_numpy=True)[0]
        a_emb = self.embedder.encode([answer], convert_to_numpy=True)[0]
        sim = np.dot(q_emb, a_emb) / (np.linalg.norm(q_emb) * np.linalg.norm(a_emb) + 1e-12)
        return float(max(0.0, min(1.0, sim)))

    def score_answer_coherence(self, answer: str) -> float:
        """Score answer coherence (simple: length penalty + sentence structure)."""
        if not answer or len(answer) < 10:
            return 0.0
        sentences = [s.strip() for s in answer.split(".") if s.strip()]
        if len(sentences) == 0:
            return 0.0
        avg_sent_len = len(answer) / len(sentences)
        if avg_sent_len < 10 or avg_sent_len > 100:
            return 0.5
        return 0.8

    def score_answer_coverage(self, answer: str, chunks: List[Dict[str, Any]]) -> float:
        """Score answer coverage of chunks (0-1)."""
        if not chunks:
            return 0.0
        chunk_ids = [c.get("id", "") for c in chunks]
        answer_lower = answer.lower()
        matched = sum(1 for cid in chunk_ids if cid.lower() in answer_lower)
        return float(min(1.0, matched / len(chunks)))

    def score_chunk_relevance_to_question(self, question: str, chunk_text: str) -> float:
        """Score chunk relevance to question (cosine similarity)."""
        q_emb = self.embedder.encode([question], convert_to_numpy=True)[0]
        c_emb = self.embedder.encode([chunk_text], convert_to_numpy=True)[0]
        sim = np.dot(q_emb, c_emb) / (np.linalg.norm(q_emb) * np.linalg.norm(c_emb) + 1e-12)
        return float(max(0.0, min(1.0, sim)))

    def score_chunk_relevance_to_answer(self, chunk_text: str, answer_text: str) -> float:
        """Score chunk relevance to answer (cosine similarity)."""
        c_emb = self.embedder.encode([chunk_text], convert_to_numpy=True)[0]
        a_emb = self.embedder.encode([answer_text], convert_to_numpy=True)[0]
        sim = np.dot(c_emb, a_emb) / (np.linalg.norm(c_emb) * np.linalg.norm(a_emb) + 1e-12)
        return float(max(0.0, min(1.0, sim)))


# ----------------------------- RAG Agent ---------------------------------------

class RAGAgent:
    """Main RAG agent orchestrating the pipeline."""

    def __init__(
        self,
        retriever: Any,  # from retriever_chroma.Retriever
        embedding_model: str = "all-MiniLM-L6-v2",
        llm_model: str = "gpt-4o-mini",
        k: int = 10,
        num_answers: int = 5,
        scoring_weights: Optional[Dict[str, float]] = None,
        max_workers: int = 4,
    ) -> None:
        self.retriever = retriever
        self.k = k
        self.num_answers = num_answers
        self.scoring_weights = scoring_weights or {"relevance": 0.4, "coherence": 0.3, "coverage": 0.3}
        self.max_workers = max_workers

        self.entity_extractor = EntityExtractor(embedding_model)
        self.answer_generator = AnswerGenerator(llm_model)
        self.chunk_scorer = ChunkScorer(embedding_model)

        logger.info(f"RAGAgent initialized with K={k}, num_answers={num_answers}, weights={self.scoring_weights}")

    def _log_step(self, step_name: str, data: Dict[str, Any]) -> None:
        """Log intermediate step data to JSON file."""
        fname = AGENT_LOG_DIR / f"step_{step_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        fname.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.debug(f"Logged step {step_name} to {fname}")

    def process(self, question: str, chat_history: Optional[List[str]] = None) -> FinalAnswer:
        """Main processing pipeline."""
        start_time = datetime.now()
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        logger.info(f"[{session_id}] Processing question: {question[:100]}...")

        # Step 1: Entity extraction
        entities = self.entity_extractor.extract_entities(question)
        keywords = [e.text for e in entities]
        self._log_step("01_entity_extraction", {"question": question, "entities": [asdict(e) for e in entities]})
        logger.info(f"Extracted {len(entities)} entities")

        # Step 2: Retrieve chunks
        chunks = self.retriever.search(question, top_k=self.k, keywords=keywords, hybrid_weight=0.7, rerank=True, chat_history=chat_history)
        self._log_step("02_retrieval", {"question": question, "retrieved_count": len(chunks), "chunk_ids": [c.get("id") for c in chunks]})
        logger.info(f"Retrieved {len(chunks)} chunks")

        if not chunks:
            logger.warning("No chunks retrieved; generating without context")
            answer_text = self.answer_generator.generate_answer(question, [])
            return FinalAnswer(answer_text=answer_text, confidence_score=0.2, top_chunks=[], original_question=question, source_chunk_ids=[])

        # Step 3: Generate 5 independent answer sets (parallel)
        answer_sets = self._generate_answer_sets_parallel(question, chunks)
        self._log_step("03_answer_generation", {"num_answers": len(answer_sets), "answers": [asdict(a) for a in answer_sets]})
        logger.info(f"Generated {len(answer_sets)} answer sets")

        # Step 4: Score answers
        scored_answers = []
        for ans in answer_sets:
            rel_score = self.chunk_scorer.score_answer_relevance(question, ans.text, chunks)
            coh_score = self.chunk_scorer.score_answer_coherence(ans.text)
            cov_score = self.chunk_scorer.score_answer_coverage(ans.text, chunks)
            combined = self.scoring_weights["relevance"] * rel_score + self.scoring_weights["coherence"] * coh_score + self.scoring_weights["coverage"] * cov_score
            scored = ScoredAnswer(text=ans.text, relevance_score=rel_score, coherence_score=coh_score, coverage_score=cov_score, combined_score=combined, source_chunk_ids=ans.source_chunk_ids)
            scored_answers.append(scored)
        scored_answers = sorted(scored_answers, key=lambda a: a.combined_score, reverse=True)
        self._log_step("04_answer_scoring", {"answers": [asdict(a) for a in scored_answers]})
        logger.info(f"Scored answers; top={scored_answers[0].combined_score:.3f}")

        # Step 5 & 6: Score chunks and select top ones
        chunk_scores: Dict[str, ScoredChunk] = {}
        for chunk in chunks:
            cid = chunk.get("id")
            ctext = chunk.get("text", "")
            q_rel = self.chunk_scorer.score_chunk_relevance_to_question(question, ctext)
            a_rels = [self.chunk_scorer.score_chunk_relevance_to_answer(ctext, a.text) for a in scored_answers]
            avg_a_rel = np.mean(a_rels) if a_rels else 0.0
            combined = 0.5 * q_rel + 0.5 * avg_a_rel
            used_count = sum(1 for a in scored_answers if cid in a.source_chunk_ids)
            chunk_scores[cid] = ScoredChunk(id=cid, text=ctext, relevance_to_question=q_rel, avg_relevance_to_answers=avg_a_rel, combined_score=combined, used_in_answers=used_count)

        top_chunks = sorted(chunk_scores.values(), key=lambda c: c.combined_score, reverse=True)[: max(3, self.k // 2)]
        self._log_step("05_chunk_scoring", {"chunks": [asdict(c) for c in top_chunks]})
        logger.info(f"Selected {len(top_chunks)} top chunks for augmented context")

        # Step 7: Augment context and generate final answer
        augmented_chunks = [{"id": c.id, "text": c.text, "score": c.combined_score} for c in top_chunks]
        final_answer_text = self.answer_generator.generate_answer(question, augmented_chunks)

        # Step 8: Return result
        confidence = (scored_answers[0].combined_score + np.mean([c.combined_score for c in top_chunks])) / 2.0
        result = FinalAnswer(
            answer_text=final_answer_text,
            confidence_score=float(confidence),
            top_chunks=[asdict(c) for c in top_chunks],
            original_question=question,
            source_chunk_ids=[c.id for c in top_chunks],
        )

        self._log_step("06_final_answer", {
            "question": question,
            "answer": final_answer_text,
            "confidence": confidence,
            "top_chunk_ids": [c.id for c in top_chunks],
            "duration_seconds": (datetime.now() - start_time).total_seconds(),
        })

        logger.info(f"[{session_id}] Processing complete (confidence={confidence:.3f})")
        return result

    def _generate_answer_sets_parallel(self, question: str, chunks: List[Dict[str, Any]]) -> List[ScoredAnswer]:
        """Generate 5 independent answer sets using different chunk combinations in parallel."""
        # create different chunk subsets (different orderings + sizes)
        chunk_combinations = []
        for i in range(self.num_answers):
            # shuffle and take different slices
            np.random.seed(i)  # reproducible shuffles
            shuffled = list(np.random.permutation(len(chunks)))  # convert to list
            size = max(2, len(chunks) // (i + 2))
            indices = shuffled[:size]
            subset = [chunks[int(j)] for j in indices]  # ensure j is int
            chunk_combinations.append(subset)

        answers = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as exe:
            futures = {exe.submit(self.answer_generator.generate_answer, question, combo): combo for combo in chunk_combinations}
            for future in as_completed(futures):
                combo = futures[future]
                try:
                    text = future.result()
                    source_ids = [c.get("id") for c in combo]
                    # placeholder scores (these will be recomputed in main pipeline)
                    answers.append(ScoredAnswer(text=text, relevance_score=0.0, coherence_score=0.0, coverage_score=0.0, combined_score=0.0, source_chunk_ids=source_ids))
                except Exception as e:
                    logger.error(f"Failed to generate answer from combo: {e}")
        return answers


# ----------------------------- CLI Runner -------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="RAG Agent pipeline")
    parser.add_argument("--question", "-q", default="What are the key benefits of the system?")
    parser.add_argument("--persist", "-p", default="chroma_store")
    parser.add_argument("--collection", "-c", default="doc_chunks")
    parser.add_argument("--k", type=int, default=10)
    parser.add_argument("--num-answers", type=int, default=5)
    args = parser.parse_args()

    # Lazy import retriever
    from retriever_chroma import Retriever

    retriever = Retriever(persist_dir=Path(args.persist), collection_name=args.collection)
    agent = RAGAgent(retriever=retriever, k=args.k, num_answers=args.num_answers)
    result = agent.process(args.question, chat_history=None)

    print("\n" + "=" * 80)
    print(f"QUESTION: {result.original_question}")
    print(f"ANSWER:\n{result.answer_text}")
    print(f"\nCONFIDENCE: {result.confidence_score:.3f}")
    print(f"SOURCE CHUNKS: {result.source_chunk_ids}")
    print("=" * 80)
