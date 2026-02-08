# RAG Chatbot Frontend + Backend

Full-stack RAG (Retrieval-Augmented Generation) chatbot application with modern React UI and Flask API backend.

## 📦 Project Structure

```
Agent_rag_front/
├── frontend/                  # React TypeScript SPA
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/            # Page components
│   │   ├── hooks/            # Custom React hooks
│   │   ├── api/              # API client
│   │   ├── styles/           # Global styles
│   │   ├── types/            # TypeScript types
│   │   ├── App.tsx           # Main app component
│   │   └── main.tsx          # Entry point
│   ├── public/               # Static assets
│   ├── package.json          # NPM dependencies
│   ├── vite.config.ts        # Vite configuration
│   ├── tailwind.config.js    # Tailwind CSS config
│   └── Dockerfile
├── backend/                   # Flask REST API
│   ├── app.py                # Main Flask application
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile
├── docker-compose.yml        # Docker Compose setup
├── package.json              # Workspace configuration
└── .env.example              # Environment variables template
```

## 🚀 Quick Start

### Option 1: Using npm (Recommended for Development)

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Set environment variables:**
   ```bash
   cp .env.example .env.local
   ```

3. **Start both frontend and backend:**
   ```bash
   npm run dev
   ```

   This will start:
   - Frontend: http://localhost:5173
   - Backend: http://localhost:5000

### Option 2: Using Docker

1. **Build and run:**
   ```bash
   docker-compose up --build
   ```

   Access the application at: http://localhost:5173

### Option 3: Run Separately

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python app.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 🔧 Configuration

Edit `.env.local` to customize:

```env
# Frontend
VITE_API_BASE_URL=http://localhost:5000
VITE_API_TIMEOUT=30000

# Backend
FLASK_ENV=development
FLASK_DEBUG=True
RAG_SYSTEM_PATH=/Users/Shared/AgenticRAG
OPENAI_API_KEY=sk-...  # Optional for better answer quality
```

## 💻 Available Scripts

### Frontend

```bash
npm run dev           # Start dev server
npm run build         # Build for production
npm run preview       # Preview production build
npm run type-check    # Run TypeScript compiler
```

### Backend

```bash
python app.py         # Run Flask server
python -m flask run --debug  # Run with auto-reload
```

### Workspace

```bash
npm run dev           # Run both frontend and backend
npm run build         # Build frontend
npm run type-check    # Check TypeScript
```

## 📡 API Endpoints

### Chat
- **POST** `/api/chat` - Send question to RAG system
  ```json
  {
    "question": "What are the main features?",
    "chat_history": ["Previous messages..."]
  }
  ```

### Documents
- **POST** `/api/upload` - Upload PDF or Markdown document
- **POST** `/api/reindex` - Rebuild vector index from all documents

### System
- **GET** `/api/health` - Health check endpoint

## 🎨 UI Components

### Header
- Navigation and action buttons
- Upload and Reindex controls
- Mobile-responsive menu

### ChatWindow
- Message display with avatars
- Loading indicators
- Empty state with instructions

### MessageItem
- User and assistant message styling
- Copy to clipboard
- Confidence score display
- Source attribution

### MessageInput
- Text area with auto-resize
- Send button with loading state
- Keyboard shortcuts (Enter to send, Shift+Enter for newline)

### FileUpload
- Drag and drop support
- Upload progress tracking
- File type validation
- Error handling

## 🔌 Integration with RAG System

The Flask backend connects to the existing RAG system at `/Users/Shared/AgenticRAG`:

- **Retriever**: Performs hybrid semantic+keyword search
- **RAG Agent**: Generates answers with multi-dimensional scoring
- **Chunker**: Processes new documents
- **Vectorstore**: Chroma-based persistent vector database

## 🎯 Features

- ✅ Real-time chat with RAG answers
- ✅ Document upload (PDF, Markdown)
- ✅ Confidence scores and source attribution
- ✅ Chat history support
- ✅ Mobile responsive UI
- ✅ Dark mode ready
- ✅ TypeScript for type safety
- ✅ Tailwind CSS for styling
- ✅ CORS enabled for development
- ✅ Docker support

## 📝 Development

### Adding a new API endpoint:

1. Create handler in `backend/app.py`
2. Create API client method in `frontend/src/api/client.ts`
3. Use in component via custom hook or direct call

### Adding a new component:

1. Create in `frontend/src/components/`
2. Define TypeScript interfaces in `frontend/src/types/`
3. Use in page or other components

## 🐛 Troubleshooting

**Backend won't start:**
- Check RAG_SYSTEM_PATH is correct
- Ensure Python 3.11+ is installed
- Run: `pip install -r backend/requirements.txt`

**Frontend won't connect to backend:**
- Check VITE_API_BASE_URL in .env
- Ensure backend is running on port 5000
- Check browser console for CORS errors

**Documents not found in chat:**
- Run the reindex endpoint: POST `/api/reindex`
- Check that documents are in `/Users/Shared/AgenticRAG/doc_dump_md/`

## 📚 Additional Resources

- [RAG System Documentation](/Users/Shared/AgenticRAG/README_RAG.md)
- [React Documentation](https://react.dev)
- [Flask Documentation](https://flask.palletsprojects.com)
- [Vite Documentation](https://vitejs.dev)
- [Tailwind CSS Documentation](https://tailwindcss.com)

## 📄 License

This project is part of the RAG Chatbot system.
