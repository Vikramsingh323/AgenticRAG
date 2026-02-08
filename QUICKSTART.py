#!/usr/bin/env python3
"""
RAG System - Quick Start Guide
===============================

The fastest way to get the RAG system running and generating answers.
"""

# ============================================================================
# OPTION 1: RUN FULL DEMO IN ONE COMMAND
# ============================================================================

# In terminal:
# $ python3 integration_demo.py

# This will:
# - Chunk 3 sample markdown files (doc_dump_md/) into 15 chunks
# - Build a Chroma vectorstore
# - Initialize retriever with hybrid search + reranking
# - Run 3 sample queries through the RAG agent
# - Output results with confidence scores
# - Save logs to agent_logs/

# Expected output:
# ✓ 3 queries successfully processed
# Confidence scores: 0.15-0.25 (without OpenAI) or higher (with API key)
# Processing time: ~3 seconds total

# ============================================================================
# OPTION 2: STEP-BY-STEP PYTHON USAGE
# ============================================================================

from pathlib import Path
from markdown_chunker import MarkdownChunker
from vectorstore_chroma import create_chroma_from_chunks
from retriever_chroma import Retriever
from rag_agent import RAGAgent

def run_rag_pipeline():
    """Complete RAG pipeline from markdown to answer."""
    
    # Step 1: Chunk markdown files
    print("1. Chunking markdown files...")
    chunker = MarkdownChunker(threshold=0.8)  # configurable threshold
    chunker.process_all_markdown_in_dir(
        Path('doc_dump_md'),
        outdir=Path('doc_dump_chunks')
    )
    # Output: 15 JSON chunks in doc_dump_chunks/
    
    # Step 2: Build vectorstore
    print("2. Building vectorstore...")
    summary = create_chroma_from_chunks(
        chunk_dir=Path('doc_dump_chunks'),
        persist_dir=Path('chroma_store'),
        collection_name='doc_chunks',
        embedding_model_name='all-MiniLM-L6-v2'
    )
    print(f"   Created vectorstore with {summary['added']} chunks")
    
    # Step 3: Initialize retriever
    print("3. Initializing retriever...")
    retriever = Retriever(
        persist_dir=Path('chroma_store'),
        collection_name='doc_chunks'
    )
    
    # Step 4: Create RAG agent
    print("4. Setting up RAG agent...")
    agent = RAGAgent(
        retriever=retriever,
        k=10,                    # retrieve 10 chunks
        num_answers=5,           # generate 5 answer sets
        scoring_weights={
            'relevance': 0.4,
            'coherence': 0.3,
            'coverage': 0.3
        },
        max_workers=4            # parallel workers
    )
    
    # Step 5: Process questions
    print("5. Processing queries...\n")
    questions = [
        "What are the main features described in the documents?",
        "How should I use this system?",
        "What are the key recommendations?"
    ]
    
    for q in questions:
        print(f"Q: {q}")
        result = agent.process(q, chat_history=None)
        
        print(f"A: {result.answer_text[:150]}...")
        print(f"   Confidence: {result.confidence_score:.3f}")
        print(f"   Sources: {', '.join(result.source_chunk_ids[:3])}")
        print()

# ============================================================================
# OPTION 3: ADVANCED USAGE WITH CUSTOM PARAMETERS
# ============================================================================

def advanced_example():
    """Example with custom parameters and chat history."""
    
    retriever = Retriever(Path('chroma_store'))
    
    # Custom retrieval with keywords
    results = retriever.search(
        query='database performance optimization',
        top_k=5,                          # fewer results
        keywords=['performance', 'index'], # boost specific terms
        hybrid_weight=0.6,                # 60% semantic, 40% keyword
        rerank=True,                      # use cross-encoder
        chat_history=[
            'User: How do databases work?',
            'Assistant: Databases store and retrieve data...'
        ]
    )
    print(f"Retrieved {len(results)} chunks")
    for i, r in enumerate(results[:3], 1):
        print(f"  {i}. {r['id']}: score={r['score']:.3f}")
    
    # Custom RAG agent with different settings
    agent = RAGAgent(
        retriever=retriever,
        k=15,                    # retrieve more chunks
        num_answers=7,           # more diverse answers
        scoring_weights={
            'relevance': 0.5,
            'coherence': 0.2,
            'coverage': 0.3
        },
        max_workers=8
    )
    
    result = agent.process(
        'Complex question about system architecture?',
        chat_history=['Previous: User asked about databases']
    )
    
    print(f"Answer: {result.answer_text}")
    print(f"Confidence: {result.confidence_score:.3f}")

# ============================================================================
# OPTION 4: USE WITH OPENAI API FOR BETTER RESULTS
# ============================================================================

# Before running, set your API key:
# export OPENAI_API_KEY=sk-...

# Then run any of the above examples. The system will automatically:
# - Use GPT-4o-mini for entity extraction
# - Use GPT-4o-mini for answer generation
# - Get higher quality answers and confidence scores

# ============================================================================
# CONFIGURABLE PARAMETERS QUICK REFERENCE
# ============================================================================

PARAMETERS = {
    "MarkdownChunker": {
        "threshold": 0.8,  # similarity threshold for merging (0-1)
        "model_name": "all-MiniLM-L6-v2"  # embedding model
    },
    "Retriever": {
        "persist_dir": "chroma_store",  # location of vectorstore
        "collection_name": "doc_chunks",  # Chroma collection name
        "embed_model": "all-MiniLM-L6-v2",  # embedding model
        "cross_encoder_model": "cross-encoder/ms-marco-MiniLM-L-6-v2",  # reranker
        "hybrid_weight": 0.7,  # semantic vs keyword (0.7 = 70% semantic)
        "top_k": 10  # number of results to return
    },
    "RAGAgent": {
        "k": 10,  # retrieval count
        "num_answers": 5,  # number of answer sets to generate
        "scoring_weights": {
            "relevance": 0.4,
            "coherence": 0.3,
            "coverage": 0.3
        },
        "max_workers": 4,  # parallel workers
        "embedding_model": "all-MiniLM-L6-v2",
        "llm_model": "gpt-4o-mini"  # used if OpenAI available
    }
}

# ============================================================================
# OUTPUT STRUCTURE
# ============================================================================

OUTPUT_STRUCTURE = {
    "FinalAnswer": {
        "answer_text": "str",  # generated answer
        "confidence_score": "float 0-1",  # overall confidence
        "top_chunks": [
            {
                "id": "chunk_id",
                "text": "chunk content",
                "combined_score": 0.85,  # relevance score
                "relevance_to_question": 0.9,
                "avg_relevance_to_answers": 0.8,
                "used_in_answers": 4  # how many of 5 answers used it
            }
        ],
        "original_question": "str",
        "source_chunk_ids": ["id1", "id2", ...]  # attribution
    },
    "agent_logs": {
        "step_01_entity_extraction_*.json": "extracted keywords",
        "step_02_retrieval_*.json": "retrieved chunks and scores",
        "step_03_answer_generation_*.json": "5 candidate answers",
        "step_04_answer_scoring_*.json": "relevance/coherence/coverage scores",
        "step_05_chunk_scoring_*.json": "chunk selection logic",
        "step_06_final_answer_*.json": "final answer with confidence"
    }
}

# ============================================================================
# TROUBLESHOOTING
# ============================================================================

TROUBLESHOOTING = {
    "ImportError: No module named 'chromadb'": [
        "pip install chromadb"
    ],
    "ImportError: No module named 'sentence_transformers'": [
        "pip install sentence-transformers"
    ],
    "CUDA out of memory": [
        "Use a smaller embedding model",
        "Reduce batch_size in vectorstore creation",
        "Disable cross-encoder reranking: Retriever(..., cross_encoder_model=None)"
    ],
    "Low confidence scores": [
        "Set OPENAI_API_KEY environment variable for better generation",
        "Check agent_logs/ to see intermediate steps",
        "Increase num_answers to generate more diverse perspectives",
        "Adjust scoring_weights to prioritize relevance"
    ],
    "Slow performance": [
        "Reduce k (retrieval count) from 10 to 5",
        "Reduce num_answers from 5 to 3",
        "Disable reranking in retriever.search(rerank=False)",
        "Use fewer max_workers"
    ]
}

# ============================================================================
# NEXT STEPS
# ============================================================================

NEXT_STEPS = """
1. Run the demo:
   python3 integration_demo.py

2. Try custom queries:
   from retriever_chroma import Retriever
   r = Retriever(Path('chroma_store'))
   results = r.search('your question here', top_k=5)

3. Analyze logs:
   ls agent_logs/
   cat agent_logs/step_06_final_answer_*.json

4. Integrate with your data:
   - Replace doc_dump_md/ with your markdown files
   - Run chunker
   - Build vectorstore
   - Query with RAG agent

5. Optimize for your use case:
   - Adjust chunking threshold
   - Tune scoring weights
   - Change embedding models
   - Experiment with hybrid_weight
   - Try different cross-encoder models
"""

# ============================================================================
# FILE REFERENCE
# ============================================================================

FILE_REFERENCE = {
    "markdown_chunker.py": "Chunk markdown with LLM strategy selection",
    "vectorstore_chroma.py": "Build Chroma vectorstore from chunks",
    "retriever_chroma.py": "Hybrid semantic+keyword retrieval with reranking",
    "rag_agent.py": "Multi-answer synthesis with comprehensive scoring",
    "integration_demo.py": "Full pipeline demo orchestrator",
    "README_RAG.md": "Detailed user guide and examples",
    "ARCHITECTURE.py": "System design and data flow documentation",
    "requirements.txt": "Python dependencies",
    "agent_logs/": "Query execution logs (6 JSON files per query)"
}

if __name__ == "__main__":
    print(__doc__)
    print("\n" + "="*80)
    print("RUN ONE OF THESE:")
    print("="*80)
    print("\n1. python3 integration_demo.py")
    print("\n2. python3 -c 'from QUICKSTART import run_rag_pipeline; run_rag_pipeline()'")
    print("\n3. python3 -c 'from QUICKSTART import advanced_example; advanced_example()'")
