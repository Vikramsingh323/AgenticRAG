# RAG Chatbot - Setup Guide

## ✅ Prerequisites

Before starting, ensure you have:

- **Python 3.11+** (already installed)
- **Node.js 18+** (not yet installed)
- **Git** (for version control)

## 🔧 Installation Steps

### Step 1: Install Node.js (if not already installed)

On macOS using Homebrew:
```bash
brew install node
```

Or download from: https://nodejs.org/

Verify installation:
```bash
node --version
npm --version
```

### Step 2: Navigate to Project Directory

```bash
cd /Users/Shared/AgenticRAG/Agent_rag_front
```

### Step 3: Install Dependencies

**Option A: Install all at once**
```bash
npm install
```

This will install:
- Root workspace dependencies (`concurrently`)
- Frontend dependencies (React, Vite, TypeScript, Tailwind)
- Backend dependencies (Flask, Flask-CORS, python-dotenv)

**Option B: Install separately**

Frontend only:
```bash
cd frontend
npm install
cd ..
```

Backend only:
```bash
pip install -r backend/requirements.txt
```

### Step 4: Configure Environment

1. Copy environment template:
```bash
cp .env.example .env.local
```

2. Edit `.env.local` with your settings:
```env
VITE_API_BASE_URL=http://localhost:5000
VITE_API_TIMEOUT=30000
FLASK_ENV=development
FLASK_DEBUG=True
RAG_SYSTEM_PATH=/Users/Shared/AgenticRAG
OPENAI_API_KEY=sk-...  # Optional
```

## 🚀 Running the Application

### Development Mode (Recommended)

Start both frontend and backend with hot reload:

```bash
npm run dev
```

This launches:
- **Frontend**: http://localhost:5173 (React dev server with hot reload)
- **Backend**: http://localhost:5000 (Flask with auto-reload)

### Manual - Run Separately

**Terminal 1 - Backend:**
```bash
cd backend
python app.py
# or with auto-reload:
python -m flask run --debug
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Docker (Optional)

Build and run with Docker Compose:
```bash
docker-compose up --build
```

Access at: http://localhost:5173

## 📁 Project Files

**Created Files:**
```
frontend/
  ├── src/
  │   ├── components/
  │   │   ├── Header.tsx           ← Top navigation bar
  │   │   ├── ChatWindow.tsx        ← Main chat interface
  │   │   ├── MessageItem.tsx       ← Individual message display
  │   │   ├── MessageInput.tsx      ← Text input area
  │   │   └── FileUpload.tsx        ← Document upload UI
  │   ├── pages/
  │   │   └── ChatBot.tsx           ← Main page component
  │   ├── hooks/
  │   │   └── useChatbot.ts         ← Chat state management
  │   ├── api/
  │   │   └── client.ts             ← API integration
  │   ├── types/
  │   │   └── index.ts              ← TypeScript interfaces
  │   ├── styles/
  │   │   └── index.css             ← Global styles
  │   ├── App.tsx                   ← Root component
  │   └── main.tsx                  ← Entry point
  ├── public/                       ← Static assets
  ├── index.html                    ← HTML template
  ├── package.json                  ← NPM configuration
  ├── tsconfig.json                 ← TypeScript config
  ├── vite.config.ts                ← Vite build config
  ├── tailwind.config.js            ← Tailwind CSS config
  ├── postcss.config.js             ← PostCSS config
  └── Dockerfile                    ← Docker image

backend/
  ├── app.py                        ← Flask application (main file)
  ├── requirements.txt              ← Python dependencies
  └── Dockerfile                    ← Docker image

Root:
  ├── package.json                  ← Workspace config
  ├── docker-compose.yml            ← Docker Compose setup
  ├── .env.example                  ← Environment template
  ├── .gitignore                    ← Git ignore rules
  └── README.md                     ← Full documentation
```

## 🎯 First Steps

1. **Start the app:**
   ```bash
   npm run dev
   ```

2. **Open in browser:**
   Go to http://localhost:5173

3. **Upload a document:**
   Click "Upload" button and select a PDF or Markdown file from `/Users/Shared/AgenticRAG/doc_dump_md/`

4. **Ask a question:**
   Type "What are the main features?" in the chat input

5. **View results:**
   See the answer with confidence score and sources

## 🔗 Integration with RAG System

The Flask backend automatically connects to:
- **Vectorstore**: `/Users/Shared/AgenticRAG/chroma_store/`
- **Chunks**: `/Users/Shared/AgenticRAG/doc_dump_chunks/`
- **Documents**: `/Users/Shared/AgenticRAG/doc_dump_md/`
- **Logs**: `/Users/Shared/AgenticRAG/agent_logs/`

All paths are configured in backend/app.py via `RAG_SYSTEM_PATH`.

## ⚡ Key Features

✨ **Real-time Chat**
- Send questions about your documents
- Get RAG-powered answers with citations
- View confidence scores

📄 **Document Management**
- Upload PDF and Markdown files
- Automatic indexing
- Reindex capability

🎨 **Modern UI**
- Responsive design (mobile-friendly)
- Message bubbles with timestamps
- Loading indicators
- Error handling

🔗 **Full Integration**
- Connected to RAG system
- Hybrid search (semantic + keyword)
- Answer scoring and attribution

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `npm: command not found` | Install Node.js: `brew install node` |
| `Backend not responding` | Check port 5000 is available: `lsof -i :5000` |
| `CORS errors in browser` | Backend CORS is enabled for development |
| `Documents not found` | Run "Reindex" button or POST `/api/reindex` |
| `Module not found` | Run `pip install -r backend/requirements.txt` |

## 📊 Development Workflow

```
1. Make code changes
2. Browser auto-reloads (Vite HMR)
3. See updates immediately
4. No manual restart needed
```

## 📚 Documentation

- **RAG System**: [README_RAG.md](../README_RAG.md)
- **Architecture**: [ARCHITECTURE.py](../ARCHITECTURE.py)
- **Frontend README**: [README.md](./README.md)

## 🎓 Next Steps

1. **Customize appearance:**
   - Edit `frontend/tailwind.config.js` for colors
   - Modify components in `frontend/src/components/`

2. **Adjust RAG parameters:**
   - Edit `backend/app.py` line ~60 for retrieval settings
   - Change `k` (number of chunks) and `num_answers` values

3. **Enable OpenAI API:**
   - Set `OPENAI_API_KEY` in `.env.local`
   - Better answer quality and confidence scores

4. **Deploy to production:**
   - Build frontend: `cd frontend && npm run build`
   - Use Docker: `docker-compose up --build`

## 💡 Tips

- **Clear chat history:** Refresh the browser (Ctrl+R / Cmd+R)
- **View API logs:** Check Flask terminal output
- **Copy answers:** Hover over message and click copy icon
- **Mobile friendly:** Works on tablets and phones

## 🚀 You're Ready!

Run this command and start chatting:

```bash
npm run dev
```

Then open: **http://localhost:5173**

---

**Questions?** Check the README.md or RAG system documentation!
