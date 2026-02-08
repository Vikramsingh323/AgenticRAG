#!/usr/bin/env python3
"""
RAG System Backend API - Flask REST API for Chatbot
====================================================

Exposes the RAG system as REST endpoints for the React frontend.
Handles question processing, streaming responses, and maintaining chat history.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from flask import Flask, request, jsonify, stream_with_context, Response
from flask_cors import CORS
from dataclasses import asdict, dataclass

from retriever_chroma import Retriever
from rag_agent import RAGAgent

# ============================================================================
# SETUP
# ============================================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Global state (in production, use proper session management)
chat_sessions: Dict[str, Any] = {}
global_retriever: Optional[Retriever] = None
global_agent: Optional[RAGAgent] = None

# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class ChatMessage:
    """Single message in chat history."""
    id: str
    role: str  # "user" or "assistant"
    content: str
    timestamp: str
    confidence_score: Optional[float] = None
    sources: Optional[List[str]] = None


@dataclass
class ChatSession:
    """Manages a chat conversation."""
    session_id: str
    messages: List[ChatMessage]
    created_at: str
    
    def to_dict(self):
        return {
            "session_id": self.session_id,
            "messages": [
                {
                    "id": m.id,
                    "role": m.role,
                    "content": m.content,
                    "timestamp": m.timestamp,
                    "confidence_score": m.confidence_score,
                    "sources": m.sources
                }
                for m in self.messages
            ],
            "created_at": self.created_at
        }


# ============================================================================
# INITIALIZATION
# ============================================================================

@app.route("/api/init", methods=["POST"])
def init_system():
    """Initialize RAG system with vectorstore and retriever."""
    global global_retriever, global_agent
    
    try:
        logger.info("Initializing RAG system...")
        
        # Initialize retriever
        global_retriever = Retriever(
            persist_dir=Path("chroma_store"),
            collection_name="doc_chunks"
        )
        logger.info("✓ Retriever initialized")
        
        # Initialize RAG agent
        global_agent = RAGAgent(
            retriever=global_retriever,
            k=10,
            num_answers=5,
            scoring_weights={
                "relevance": 0.4,
                "coherence": 0.3,
                "coverage": 0.3
            },
            max_workers=4
        )
        logger.info("✓ RAG Agent initialized")
        
        return jsonify({
            "success": True,
            "message": "RAG system initialized successfully",
            "status": "ready"
        }), 200
    
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        return jsonify({
            "success": False,
            "message": str(e),
            "status": "error"
        }), 500


# ============================================================================
# CHAT SESSION MANAGEMENT
# ============================================================================

@app.route("/api/session/create", methods=["POST"])
def create_session():
    """Create a new chat session."""
    import uuid
    session_id = str(uuid.uuid4())
    chat_sessions[session_id] = ChatSession(
        session_id=session_id,
        messages=[],
        created_at=datetime.now().isoformat()
    )
    logger.info(f"Created session: {session_id}")
    return jsonify({
        "success": True,
        "session_id": session_id,
        "created_at": chat_sessions[session_id].created_at
    }), 200


@app.route("/api/session/<session_id>/messages", methods=["GET"])
def get_session_messages(session_id: str):
    """Get all messages in a session."""
    if session_id not in chat_sessions:
        return jsonify({"success": False, "message": "Session not found"}), 404
    
    session = chat_sessions[session_id]
    return jsonify({
        "success": True,
        "session_id": session_id,
        "messages": session.to_dict()["messages"]
    }), 200


@app.route("/api/session/<session_id>/clear", methods=["POST"])
def clear_session(session_id: str):
    """Clear all messages in a session."""
    if session_id not in chat_sessions:
        return jsonify({"success": False, "message": "Session not found"}), 404
    
    chat_sessions[session_id].messages = []
    logger.info(f"Cleared session: {session_id}")
    return jsonify({"success": True, "message": "Session cleared"}), 200


# ============================================================================
# MAIN CHAT ENDPOINT
# ============================================================================

@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Main chat endpoint. Processes user question through RAG pipeline.
    
    Request body:
    {
        "session_id": "...",
        "message": "user question",
        "stream": true/false
    }
    """
    if global_agent is None:
        return jsonify({
            "success": False,
            "message": "RAG system not initialized. Call /api/init first."
        }), 500
    
    try:
        data = request.json
        session_id = data.get("session_id")
        user_message = data.get("message", "").strip()
        stream = data.get("stream", False)
        
        if not session_id or session_id not in chat_sessions:
            return jsonify({"success": False, "message": "Invalid session"}), 400
        
        if not user_message:
            return jsonify({"success": False, "message": "Empty message"}), 400
        
        session = chat_sessions[session_id]
        
        # Add user message to history
        import uuid
        user_msg_id = str(uuid.uuid4())
        user_msg = ChatMessage(
            id=user_msg_id,
            role="user",
            content=user_message,
            timestamp=datetime.now().isoformat()
        )
        session.messages.append(user_msg)
        logger.info(f"Session {session_id}: User message '{user_message[:50]}...'")
        
        # Build chat history for RAG agent
        chat_history = [
            f"{m.role.capitalize()}: {m.content}"
            for m in session.messages[:-1]  # exclude current user message
        ]
        
        # Process through RAG agent
        logger.info(f"Processing question through RAG pipeline...")
        rag_result = global_agent.process(user_message, chat_history=chat_history)
        
        # Add assistant message to history
        assistant_msg_id = str(uuid.uuid4())
        assistant_msg = ChatMessage(
            id=assistant_msg_id,
            role="assistant",
            content=rag_result.answer_text,
            timestamp=datetime.now().isoformat(),
            confidence_score=float(rag_result.confidence_score),
            sources=rag_result.source_chunk_ids[:5]  # top 5 sources
        )
        session.messages.append(assistant_msg)
        
        logger.info(f"Answer generated with confidence: {rag_result.confidence_score:.3f}")
        
        # Return response
        return jsonify({
            "success": True,
            "session_id": session_id,
            "user_message": {
                "id": user_msg_id,
                "role": "user",
                "content": user_message,
                "timestamp": user_msg.timestamp
            },
            "assistant_message": {
                "id": assistant_msg_id,
                "role": "assistant",
                "content": rag_result.answer_text,
                "timestamp": assistant_msg.timestamp,
                "confidence_score": float(rag_result.confidence_score),
                "sources": rag_result.source_chunk_ids[:5],
                "top_chunks": [
                    {
                        "id": chunk["id"],
                        "text": chunk["text"][:200],  # truncate for frontend
                        "score": float(chunk.get("combined_score", 0)),
                        "relevance": float(chunk.get("relevance_to_question", 0))
                    }
                    for chunk in rag_result.top_chunks[:3]
                ]
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "message": f"Error processing message: {str(e)}"
        }), 500


# ============================================================================
# SEARCH/RETRIEVAL ENDPOINT
# ============================================================================

@app.route("/api/search", methods=["POST"])
def search():
    """
    Direct search in vectorstore without full RAG pipeline.
    Useful for quick lookups.
    
    Request body:
    {
        "query": "search query",
        "top_k": 5
    }
    """
    if global_retriever is None:
        return jsonify({
            "success": False,
            "message": "Retriever not initialized"
        }), 500
    
    try:
        data = request.json
        query = data.get("query", "").strip()
        top_k = data.get("top_k", 5)
        
        if not query:
            return jsonify({"success": False, "message": "Empty query"}), 400
        
        logger.info(f"Search query: {query}")
        results = global_retriever.search(query=query, top_k=top_k, rerank=True)
        
        return jsonify({
            "success": True,
            "query": query,
            "results": [
                {
                    "id": r.get("id"),
                    "text": r.get("text")[:300],
                    "score": float(r.get("score", 0)),
                    "metadata": r.get("metadata", {})
                }
                for r in results
            ]
        }), 200
    
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# ============================================================================
# SYSTEM STATUS ENDPOINT
# ============================================================================

@app.route("/api/status", methods=["GET"])
def status():
    """Get system status and statistics."""
    return jsonify({
        "success": True,
        "status": "running",
        "backend": "Flask + RAG System",
        "initialized": global_agent is not None,
        "active_sessions": len(chat_sessions),
        "total_messages": sum(len(s.messages) for s in chat_sessions.values()),
        "timestamp": datetime.now().isoformat()
    }), 200


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.route("/health", methods=["GET"])
def health():
    """Simple health check."""
    return jsonify({"status": "ok"}), 200


# ============================================================================
# ERROR HANDLING
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "message": "Endpoint not found"}), 404


@app.errorhandler(500)
def server_error(error):
    logger.error(f"Server error: {error}")
    return jsonify({"success": False, "message": "Internal server error"}), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    logger.info("Starting RAG Backend API...")
    logger.info("Available endpoints:")
    logger.info("  POST /api/init - Initialize RAG system")
    logger.info("  POST /api/session/create - Create new chat session")
    logger.info("  GET  /api/session/<id>/messages - Get session messages")
    logger.info("  POST /api/session/<id>/clear - Clear session")
    logger.info("  POST /api/chat - Send message to chatbot")
    logger.info("  POST /api/search - Search vectorstore")
    logger.info("  GET  /api/status - System status")
    logger.info("  GET  /health - Health check")
    
    app.run(debug=True, host="0.0.0.0", port=5000)
