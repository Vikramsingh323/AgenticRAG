#!/usr/bin/env python3
"""
RAG System Components Summary
=============================

This file provides a high-level overview of the complete RAG (Retrieval-Augmented Generation)
system architecture, components, and their interactions.

## System Architecture Diagram

    Input Markdown Files (doc_dump_md/)
              |
              v
    [markdown_chunker.py]
         (Entity extraction + LLM strategy selection + 3 chunking methods)
              |
              v
    Output: JSON Chunks (doc_dump_chunks/)
              |
              v
    [vectorstore_chroma.py]
         (Embedding computation + Chroma persistence)
              |
              v
    Output: Vector DB (chroma_store/)
              |
              v
    [retriever_chroma.py]
         (Hybrid semantic+keyword search + reranking)
              |
              v
    [rag_agent.py] ← Main Orchestrator
    ├─ EntityExtractor     (keyword extraction)
    ├─ AnswerGenerator     (LLM-based synthesis)
    ├─ ChunkScorer        (multi-dimensional scoring)
    └─ RAGAgent           (pipeline coordination)
              |
              v
    Output: Final Answer + Confidence + Attribution
              |
              v
    [agent_logs/] ← Comprehensive Step-by-Step Logs
         (6 JSON files per query showing all intermediate results)

## Component Details

### markdown_chunker.py
**Purpose**: Transform markdown documents into semantically coherent chunks

**Key Classes**:
- `MarkdownHeaderTextSplitter` — Splits text at markdown headers
- `MarkdownChunker` — Main orchestrator supporting:
  - `analyze_with_llm()` — Strategy recommendation (header/semantic/hybrid)
  - `header_chunk()` — Header-based splitting
  - `semantic_chunk()` — Paragraph-level semantic clustering with merging
  - `hybrid_chunk()` — Combines both approaches
  - `process_markdown_file()` — Single file processing
  - `process_all_markdown_in_dir()` — Batch processing

**Inputs**: Markdown files (*.md) from doc_dump_md/
**Outputs**: JSON chunk files in doc_dump_chunks/
**Configurable**:
- `threshold` (0.8 default) — Similarity threshold for merging semantic chunks
- `strategy` (None default) — Force specific strategy or auto-detect

### vectorstore_chroma.py
**Purpose**: Build and persist a vector index with embeddings

**Key Functions**:
- `create_chroma_from_chunks()` — Main entry point
  - Loads chunk JSONs
  - Computes sentence-transformers embeddings in batches
  - Handles metadata flattening (Chroma constraints)
  - Creates/replaces Chroma collection
  - Returns summary dict

**Inputs**: Chunk JSON files from doc_dump_chunks/
**Outputs**: Persistent Chroma vectorstore at chroma_store/
**Configurable**:
- `batch_size` (64 default) — Embedding batch size
- `embedding_model_name` (all-MiniLM-L6-v2 default) — Sentence-transformers model

### retriever_chroma.py
**Purpose**: Retrieve and rank relevant chunks using hybrid search

**Key Classes**:
- `Hit` — Dataclass for a single search result
- `Retriever` — Main class with methods:
  - `upsert_chunk()` — Add/update single chunk
  - `_semantic_candidates()` — Get top candidates via Chroma
  - `search()` — Hybrid search with reranking
    - Parameters:
      - `query` (str) — User question
      - `keywords` (list, optional) — Explicit keywords to boost
      - `hybrid_weight` (0.7 default) — Semantic vs keyword balance
      - `rerank` (True default) — Apply cross-encoder reranking
      - `chat_history` (optional) — Previous messages for context

**Inputs**: User question, optional keywords and chat history
**Outputs**: List of dicts with: id, text, metadata, score, sem_score, keyword_score
**Configurable**:
- `persist_dir` — Chroma storage location
- `collection_name` — Chroma collection name
- `embed_model` — Sentence-transformers model for query embedding
- `cross_encoder_model` — Cross-encoder for reranking (can be None)

### rag_agent.py
**Purpose**: Multi-stage answer synthesis with comprehensive scoring and logging

**Key Classes**:

#### EntityExtractor
- `extract_entities()` — Extract keywords from question (TF-based heuristic)
- `compute_question_embedding()` — Get question embedding for scorer

#### AnswerGenerator
- `generate_answer()` — Create answer from chunks + question
  - Uses OpenAI if available + has API key
  - Falls back to mock generation if not
  - Inputs: question, list of chunks
  - Outputs: answer string

#### ChunkScorer
- `score_answer_relevance()` — Question-answer similarity (cosine)
- `score_answer_coherence()` — Sentence structure quality heuristic
- `score_answer_coverage()` — Chunk mention coverage in answer
- `score_chunk_relevance_to_question()` — Chunk-question similarity
- `score_chunk_relevance_to_answer()` — Chunk-answer similarity

#### RAGAgent (Orchestrator)
- `process()` — Main processing pipeline:
  1. Extract entities from question
  2. Retrieve K chunks via hybrid search
  3. Generate 5 independent answer sets (parallel)
  4. Score all 5 answers
  5. Score all chunks (against question + all 5 answers)
  6. Select top chunks by combined score
  7. Generate final answer with augmented context
  8. Return FinalAnswer with confidence and attribution
  9. Log all steps to agent_logs/

**Logging**: Each step saved as JSON with timestamps:
- Step 1: Entity extraction results
- Step 2: Retrieved chunk IDs and scores
- Step 3: 5 generated answers
- Step 4: Answer scores (relevance, coherence, coverage)
- Step 5: Chunk scores and final selection
- Step 6: Final answer, confidence, duration

**Configurable**:
- `k` (10 default) — Retrieval count
- `num_answers` (5 default) — Number of independent answer sets
- `scoring_weights` — How to combine answer quality dimensions
- `max_workers` (4 default) — Parallel workers for answer generation

## Data Flow

### 1. Document Ingestion
```
Input: *.md files
↓
MarkdownChunker.process_all_markdown_in_dir()
  - Extract entities and intent
  - Select strategy (header/semantic/hybrid via LLM or heuristic)
  - Apply strategy to split markdown
  - Save chunks as JSON with metadata
↓
Output: JSON chunk files (15 total for demo)
```

### 2. Vectorization
```
Input: JSON chunks
↓
create_chroma_from_chunks()
  - Load all chunk JSON
  - Compute embeddings in batches
  - Flatten metadata (remove nested dicts, None values)
  - Store in Chroma with embeddings
↓
Output: Persistent Chroma database
```

### 3. Retrieval
```
Input: User question
↓
Retriever.search()
  - Extract query embedding
  - Get top K semantic candidates from Chroma
  - Compute keyword scores
  - Blend semantic + keyword (hybrid)
  - (Optional) Rerank with cross-encoder
  - Return top K results with scores
↓
Output: 10 ranked chunk results
```

### 4. Answer Synthesis
```
Input: Question + 10 chunks
↓
RAGAgent.process()
  - Extract entities/keywords
  - Generate 5 answers in parallel (each from different chunk subset)
  - Score all 5 on: relevance, coherence, coverage
  - Score each chunk on: relevance-to-question, avg-relevance-to-answers, usage-frequency
  - Select top 5 chunks by combined score
  - Generate final answer from top chunks + original question
  - Compute confidence as average of answer + chunk scores
  - Return FinalAnswer with: text, confidence, sources, attribution
  - Save all steps to agent_logs/ as JSON
↓
Output: FinalAnswer object + 6 JSON logs
```

## Key Design Decisions

1. **Multi-Answer Generation**: 
   - Generate 5 diverse answers to avoid single-perspective bias
   - Use different chunk combinations for diversity
   - Score and synthesize to find best supported answer

2. **Hybrid Search**:
   - Semantic: Captures meaning even with different wording
   - Keyword: Catches exact matches and specific entities
   - Weighted blend: Tunable (default 70% semantic, 30% keyword)
   - Reranking: Use cross-encoder for context-aware ranking

3. **Multi-Dimensional Scoring**:
   - Answer relevance: Does it address the question?
   - Answer coherence: Is it well-structured?
   - Answer coverage: Does it use provided chunks?
   - Chunk relevance (Q): Is it topically relevant to question?
   - Chunk relevance (A): Does it support the answers?
   - Chunk usage: How many answer sets used it?

4. **Parallel Processing**:
   - Generate 5 answers concurrently (ThreadPoolExecutor)
   - Scales with max_workers parameter
   - Each answer independent, no ordering dependency

5. **Comprehensive Logging**:
   - 6 JSON logs per query capture full processing
   - Useful for debugging, auditing, analysis
   - Timestamped and organized by step
   - Can be analyzed separately for insights

## Dependencies

- **sentence-transformers**: Embeddings (all-MiniLM-L6-v2, ms-marco cross-encoder)
- **chromadb**: Vector database persistence
- **numpy**: Numerical computations (cosine similarity, array operations)
- **PyPDF2**: (from earlier pipeline) PDF text extraction
- **openai**: (optional) GPT-4o-mini for answer generation
- **torch, transformers, huggingface-hub**: (dependencies of sentence-transformers)

## Performance Characteristics

| Operation | Time (approx) | Bottleneck |
|-----------|---------------|-----------|
| Entity extraction | 0.01s | String processing |
| Retrieval (10 chunks) | 0.1s | Chroma query + cross-encoder |
| Answer generation (5x) | 0.3s | OpenAI API or fallback |
| Chunk scoring | 0.5s | Embeddings computation |
| Total end-to-end | 0.9s | Answer generation |

## Extensibility Points

1. **Different Chunking Strategies**:
   - Add custom method to MarkdownChunker
   - Implement `def my_chunk(text: str) -> List[Chunk]`

2. **Alternative Retrievers**:
   - Replace Chroma with other vector DBs (Pinecone, Weaviate, FAISS)
   - Implement same interface as retriever_chroma.py

3. **Custom Scorers**:
   - Extend ChunkScorer with domain-specific metrics
   - Implement LLM-based relevance scoring

4. **Different LLMs**:
   - Modify AnswerGenerator to use Claude, Gemini, or local models
   - Just update the API calls in generate_answer()

5. **Alternative Embeddings**:
   - Change embedding_model parameter to any HuggingFace model
   - Options: `all-mpnet-base-v2`, `bge-large-en-v1.5`, etc.

## Testing & Validation

Run integration demo:
```bash
python3 integration_demo.py
```

This will:
1. Chunk 3 sample markdown files → 15 chunks
2. Build Chroma vectorstore → 15 vectors
3. Initialize retriever with cross-encoder
4. Run 3 sample queries through full RAG pipeline
5. Print results with confidence scores
6. Save 18 JSON logs (6 per query) to agent_logs/

Expected output: All 3 queries should complete successfully with confidence 0.1-0.3
(lower due to fallback answer generation without OpenAI API)

---

For detailed usage examples, see [README_RAG.md](README_RAG.md)
"""
