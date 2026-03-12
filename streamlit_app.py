import os
from pathlib import Path
import tempfile
import requests
import streamlit as st

from extract_pdfs import extract_text_from_pdf
from markdown_chunker import MarkdownChunker
from vectorstore_chroma import create_chroma_from_chunks


ROOT = Path(__file__).parent
RAG_PATH = ROOT
UPLOADS = RAG_PATH / 'uploads'
MD_DIR = RAG_PATH / 'doc_dump_md'
CHUNK_DIR = RAG_PATH / 'doc_dump_chunks'
VSTORE_DIR = RAG_PATH / 'chroma_store'

for d in (UPLOADS, MD_DIR, CHUNK_DIR, VSTORE_DIR):
    d.mkdir(parents=True, exist_ok=True)


st.title('AgenticRAG — Upload & Index (Streamlit)')

st.markdown('Upload a PDF/Markdown/Text file to convert to Markdown, chunk, embed and index into the vectorstore.')

uploaded = st.file_uploader('Choose a file', type=['pdf', 'md', 'markdown', 'txt'])

if uploaded is not None:
    filename = uploaded.name
    ext = filename.lower().rsplit('.', 1)[-1]
    save_path = UPLOADS / filename
    with open(save_path, 'wb') as f:
        f.write(uploaded.getbuffer())
    st.success(f'Saved upload to {save_path}')

    if ext == 'pdf':
        st.info('Converting PDF to Markdown (docling -> PyMuPDF -> PyPDF2)')
        md_filename = filename.replace('.pdf', '.md')
        md_path = MD_DIR / md_filename
        try:
            extract_text_from_pdf(save_path, md_path)
            st.success(f'Wrote markdown: {md_path}')
        except Exception as e:
            st.error(f'Conversion failed: {e}')
    elif ext in {'md', 'markdown'}:
        md_path = MD_DIR / filename
        with open(md_path, 'wb') as f:
            f.write(uploaded.getbuffer())
        st.success(f'Copied markdown to {md_path}')
    else:
        # txt
        md_filename = Path(filename).stem + '.md'
        md_path = MD_DIR / md_filename
        with open(md_path, 'wb') as f:
            f.write(uploaded.getbuffer())
        st.success(f'Converted text to markdown: {md_path}')

    # Chunking
    st.info('Chunking document...')
    chunker = MarkdownChunker(threshold=0.8)
    try:
        out = chunker.process_markdown_file(md_path, outdir=CHUNK_DIR)
        st.success(f'Created {len(out)} chunk(s)')
    except Exception as e:
        st.error(f'Chunking failed: {e}')

    # Indexing
    st.info('Indexing into Chroma vectorstore...')
    try:
        res = create_chroma_from_chunks(chunk_dir=CHUNK_DIR, persist_dir=VSTORE_DIR, collection_name='doc_chunks')
        st.success(f"Indexed: {res.get('added', 0)} items")
    except Exception as e:
        st.error(f'Indexing failed: {e}')

st.header('Chat (uses backend /api/chat)')
question = st.text_input('Ask a question about the uploaded documents')
if st.button('Send') and question:
    try:
        api_url = os.environ.get('RAG_API_URL', 'http://localhost:5001')
        r = requests.post(f"{api_url}/api/chat", json={"question": question, "chat_history": []}, timeout=30)
        if r.status_code == 200:
            data = r.json()
            st.markdown('**Answer:**')
            st.markdown(data.get('answer_text', ''))
            st.markdown('**Confidence:** ' + str(data.get('confidence_score', 0.0)))
            st.markdown('**Top Chunks:**')
            for c in data.get('top_chunks', []):
                st.markdown(f"- **{c.get('id')}** (score={c.get('combined_score'):.3f})\n\n{c.get('text', '')[:400]}")
        else:
            st.error(f'Chat API returned {r.status_code}: {r.text}')
    except Exception as e:
        st.error(f'Failed to call chat API: {e}')
