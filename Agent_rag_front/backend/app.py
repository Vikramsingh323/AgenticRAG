import os
import sys
import logging
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Add RAG system to path
RAG_PATH = Path(os.environ.get('RAG_SYSTEM_PATH', '/Users/Shared/AgenticRAG'))
sys.path.insert(0, str(RAG_PATH))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global RAG components
rag_agent = None
retriever = None
rag_initialized = False
rag_init_error = None

# Try importing RAG modules with error handling
try:
    from rag_agent import RAGAgent
    from retriever_chroma import Retriever
    from vectorstore_chroma import create_chroma_from_chunks
    from markdown_chunker import MarkdownChunker
    logger.info("RAG modules imported successfully")
except ImportError as e:
    logger.warning(f"Could not import RAG modules: {e}. RAG features will be limited.")
    RAGAgent = None
    Retriever = None
    create_chroma_from_chunks = None
    MarkdownChunker = None

def initialize_rag_system():
    """Initialize RAG components from existing vectorstore."""
    global rag_agent, retriever, rag_initialized, rag_init_error
    
    if rag_initialized:
        return rag_init_error is None
    
    try:
        if not RAGAgent or not Retriever:
            rag_init_error = "RAG modules not available"
            logger.error(rag_init_error)
            return False
        
        logger.info("Initializing RAG system...")
        
        # Check if vectorstore exists
        chroma_path = RAG_PATH / 'chroma_store'
        if not chroma_path.exists():
            rag_init_error = f"Vectorstore not found at {chroma_path}"
            logger.warning(rag_init_error)
            rag_initialized = True
            return False
        
        # Initialize retriever with existing vectorstore
        retriever = Retriever(
            persist_dir=str(chroma_path),
            collection_name='doc_chunks'
        )
        
        # Initialize RAG agent
        rag_agent = RAGAgent(
            retriever=retriever,
            k=10,
            num_answers=5,
            max_workers=4
        )
        
        logger.info("RAG system initialized successfully")
        rag_initialized = True
        rag_init_error = None
        return True
    except Exception as e:
        rag_init_error = f"Failed to initialize RAG system: {str(e)}"
        logger.error(rag_init_error, exc_info=True)
        rag_initialized = True
        return False

# Initialize on startup
@app.before_request
def startup():
    global rag_agent, rag_initialized
    if not rag_initialized:
        initialize_rag_system()

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy' if (rag_initialized and rag_agent) else ('initializing' if not rag_initialized else 'degraded'),
        'version': '1.0.0',
        'rag_initialized': rag_initialized,
        'rag_available': rag_agent is not None,
        'error': rag_init_error if rag_init_error else None
    }), 200 if (rag_initialized and rag_agent) else 503

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat endpoint for RAG queries."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        question = data.get('question', '').strip()
        chat_history = data.get('chat_history', [])
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        if not rag_agent:
            return jsonify({
                'error': 'RAG system not available',
                'status': 'uninitialized',
                'details': rag_init_error or 'Unknown error'
            }), 503
        
        logger.info(f"Processing question: {question}")
        
        try:
            # Get RAG response
            result = rag_agent.process(
                question,
                chat_history=chat_history if chat_history else None
            )
            
            # Ensure confidence score is a float
            confidence = float(result.confidence_score) if hasattr(result, 'confidence_score') else 0.0
            
            return jsonify({
                'answer_text': str(result.answer_text) if hasattr(result, 'answer_text') else '',
                'confidence_score': confidence,
                'source_chunk_ids': result.source_chunk_ids if hasattr(result, 'source_chunk_ids') else [],
                'top_chunks': [
                    {
                        'id': chunk.get('id', ''),
                        'text': chunk.get('text', '')[:200],
                        'combined_score': float(chunk.get('combined_score', 0.0))
                    }
                    for chunk in (result.top_chunks if hasattr(result, 'top_chunks') else [])[:3]
                ]
            }), 200
        
        except Exception as rag_error:
            logger.error(f"RAG processing error: {rag_error}", exc_info=True)
            return jsonify({
                'error': 'Failed to process question',
                'details': str(rag_error)
            }), 500
    
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}", exc_info=True)
        return jsonify({
            'error': 'Chat request failed',
            'details': str(e)
        }), 500

@app.route('/api/upload', methods=['POST'])
def upload():
    """Upload document, convert to markdown, create embeddings, and index."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        allowed_extensions = {'pdf', 'md', 'txt', 'markdown'}
        file_ext = file.filename.lower().split('.')[-1]
        if file_ext not in allowed_extensions:
            return jsonify({'error': f'File type not supported. Allowed: {", ".join(allowed_extensions)}'}), 400
        
        # Step 1: Save uploaded file temporarily
        upload_dir = RAG_PATH / 'uploads'
        upload_dir.mkdir(exist_ok=True, parents=True)
        
        safe_filename = os.path.basename(file.filename)
        uploaded_filepath = upload_dir / safe_filename
        
        try:
            file.save(str(uploaded_filepath))
            file_size = os.path.getsize(uploaded_filepath)
            logger.info(f"File uploaded: {safe_filename} ({file_size} bytes)")
        except Exception as save_error:
            logger.error(f"Failed to save file: {save_error}")
            return jsonify({'error': f'Failed to save file: {str(save_error)}'}), 500
        
        try:
            # Step 2: Convert to markdown if needed
            md_dir = RAG_PATH / 'doc_dump_md'
            md_dir.mkdir(exist_ok=True, parents=True)
            
            if file_ext == 'pdf':
                # For PDF files, try to convert to markdown
                logger.info(f"Converting PDF to markdown: {safe_filename}")
                md_filename = safe_filename.replace('.pdf', '.md')
                md_filepath = md_dir / md_filename
                
                try:
                    # Try using pymupdf or pypdf to extract text
                    try:
                        import fitz  # PyMuPDF
                        doc = fitz.open(str(uploaded_filepath))
                        text = ""
                        for page in doc:
                            text += page.get_text()
                        doc.close()
                    except ImportError:
                        # Fallback: try using pypdf
                        try:
                            from PyPDF2 import PdfReader
                            reader = PdfReader(str(uploaded_filepath))
                            text = ""
                            for page in reader.pages:
                                text += page.extract_text()
                        except ImportError:
                            # If neither library is available, return error
                            return jsonify({
                                'error': 'PDF processing not available. Please install PyMuPDF or PyPDF2.',
                                'filename': safe_filename
                            }), 503
                    
                    # Write as markdown
                    with open(str(md_filepath), 'w', encoding='utf-8') as f:
                        f.write(f"# {safe_filename}\n\n")
                        f.write(text)
                    
                    logger.info(f"PDF converted to markdown: {md_filename}")
                    md_file_to_index = md_filename
                
                except Exception as pdf_error:
                    logger.error(f"Failed to convert PDF: {pdf_error}")
                    return jsonify({'error': f'Failed to convert PDF: {str(pdf_error)}'}), 500
            
            elif file_ext in {'md', 'markdown'}:
                # Already markdown, just copy to the right location
                logger.info(f"Copying markdown file: {safe_filename}")
                md_filename = safe_filename if safe_filename.endswith('.md') else safe_filename + '.md'
                md_filepath = md_dir / md_filename
                
                try:
                    import shutil
                    shutil.copy(str(uploaded_filepath), str(md_filepath))
                    logger.info(f"Markdown file copied: {md_filename}")
                    md_file_to_index = md_filename
                except Exception as copy_error:
                    logger.error(f"Failed to copy markdown: {copy_error}")
                    return jsonify({'error': f'Failed to copy file: {str(copy_error)}'}), 500
            
            else:  # txt or other text formats
                # Convert txt to markdown
                logger.info(f"Converting text file to markdown: {safe_filename}")
                md_filename = safe_filename.rsplit('.', 1)[0] + '.md'
                md_filepath = md_dir / md_filename
                
                try:
                    with open(str(uploaded_filepath), 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    with open(str(md_filepath), 'w', encoding='utf-8') as f:
                        f.write(f"# {safe_filename}\n\n")
                        f.write(content)
                    
                    logger.info(f"Text converted to markdown: {md_filename}")
                    md_file_to_index = md_filename
                except Exception as txt_error:
                    logger.error(f"Failed to convert text: {txt_error}")
                    return jsonify({'error': f'Failed to convert text: {str(txt_error)}'}), 500
            
            # Step 3: Create chunks and embeddings
            if not MarkdownChunker or not create_chroma_from_chunks:
                return jsonify({
                    'error': 'RAG system not available',
                    'details': 'Required modules not loaded'
                }), 503
            
            logger.info(f"Creating chunks and embeddings for: {md_file_to_index}")
            
            try:
                # Run chunker on the new markdown file
                chunker = MarkdownChunker(threshold=0.8)
                chunk_output_dir = RAG_PATH / 'doc_dump_chunks'
                chunk_output_dir.mkdir(exist_ok=True, parents=True)
                
                # Process only the new file
                chunker.process_all_markdown_in_dir(
                    str(md_dir),
                    outdir=str(chunk_output_dir)
                )
                logger.info("Chunking completed")
                
                # Step 4: Rebuild vectorstore with all documents
                logger.info("Creating embeddings and indexing...")
                vectorstore_dir = RAG_PATH / 'chroma_store'
                vectorstore_dir.mkdir(exist_ok=True, parents=True)
                
                create_chroma_from_chunks(
                    chunk_dir=str(chunk_output_dir),
                    persist_dir=str(vectorstore_dir),
                    collection_name='doc_chunks'
                )
                logger.info("Vectorstore indexed successfully")
                
                # Step 5: Reinitialize RAG system
                global rag_agent, rag_initialized, rag_init_error
                rag_initialized = False
                initialize_rag_system()
                
                return jsonify({
                    'message': 'Document uploaded and indexed successfully',
                    'filename': safe_filename,
                    'markdown_file': md_file_to_index,
                    'size': file_size,
                    'status': 'indexed'
                }), 200
            
            except Exception as index_error:
                logger.error(f"Failed to create embeddings: {index_error}", exc_info=True)
                return jsonify({
                    'error': 'Failed to index document',
                    'details': str(index_error)
                }), 500
        
        except Exception as process_error:
            logger.error(f"Document processing error: {process_error}", exc_info=True)
            return jsonify({
                'error': 'Failed to process document',
                'details': str(process_error)
            }), 500
    
    except Exception as e:
        logger.error(f"Upload error: {e}", exc_info=True)
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/api/reindex', methods=['POST'])
def reindex():
    """Rebuild vectorstore from all documents."""
    try:
        if not MarkdownChunker or not create_chroma_from_chunks:
            return jsonify({
                'error': 'Reindexing not available',
                'details': 'Required RAG modules not loaded'
            }), 503
        
        logger.info("Starting reindexing process...")
        
        # Check if doc directories exist
        doc_dir = RAG_PATH / 'doc_dump_md'
        if not doc_dir.exists():
            logger.warning(f"Document directory not found: {doc_dir}")
            return jsonify({
                'error': 'Document directory not found',
                'path': str(doc_dir),
                'hint': 'Upload documents first before reindexing'
            }), 404
        
        # Count markdown files
        md_files = list(doc_dir.glob('*.md'))
        if not md_files:
            logger.warning(f"No markdown files found in {doc_dir}")
            return jsonify({
                'error': 'No documents to index',
                'path': str(doc_dir),
                'count': 0
            }), 404
        
        logger.info(f"Found {len(md_files)} markdown files to process")
        
        try:
            # Run chunker
            logger.info("Running markdown chunker...")
            chunker = MarkdownChunker(threshold=0.8)
            chunk_output_dir = RAG_PATH / 'doc_dump_chunks'
            chunk_output_dir.mkdir(exist_ok=True, parents=True)
            
            # Clear old chunks first
            import shutil
            if chunk_output_dir.exists():
                shutil.rmtree(str(chunk_output_dir))
                chunk_output_dir.mkdir(exist_ok=True, parents=True)
            
            chunker.process_all_markdown_in_dir(
                str(doc_dir),
                outdir=str(chunk_output_dir)
            )
            
            chunk_files = list(chunk_output_dir.glob('*.json'))
            logger.info(f"Chunking completed. Created {len(chunk_files)} chunk files")
            
            # Rebuild vectorstore
            logger.info("Rebuilding vectorstore...")
            vectorstore_dir = RAG_PATH / 'chroma_store'
            
            # Clear old vectorstore
            if vectorstore_dir.exists():
                shutil.rmtree(str(vectorstore_dir))
            vectorstore_dir.mkdir(exist_ok=True, parents=True)
            
            create_chroma_from_chunks(
                chunk_dir=str(chunk_output_dir),
                persist_dir=str(vectorstore_dir),
                collection_name='doc_chunks'
            )
            logger.info("Vectorstore rebuilt successfully")
            
            # Reinitialize RAG components
            global rag_agent, rag_initialized, rag_init_error
            rag_initialized = False
            initialize_rag_system()
            
            return jsonify({
                'message': 'Documents reindexed successfully',
                'status': 'completed',
                'documents_processed': len(md_files),
                'chunks_created': len(chunk_files),
                'vectorstore_path': str(vectorstore_dir)
            }), 200
        
        except Exception as process_error:
            logger.error(f"Reindexing process error: {process_error}", exc_info=True)
            return jsonify({
                'error': 'Reindexing failed',
                'details': str(process_error)
            }), 500
    
    except Exception as e:
        logger.error(f"Reindex error: {e}", exc_info=True)
        return jsonify({
            'error': 'Reindex request failed',
            'details': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(
        debug=os.environ.get('FLASK_DEBUG', True),
        host='0.0.0.0',
        port=5000
    )
