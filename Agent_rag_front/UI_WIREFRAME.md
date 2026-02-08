/*
  RAG CHATBOT - UI WIREFRAME & COMPONENT LAYOUT
  =============================================

  This file shows the exact structure and components of the frontend.
*/

// ============================================================================
// FULL PAGE LAYOUT
// ============================================================================

┌─────────────────────────────────────────────────────────────────────────────┐
│                          HEADER COMPONENT                                   │
│  ┌──────────────┬──────────────────────────────────────┬──────────────────┐│
│  │ ☰ | 💬 RAG  │  RAG Chatbot - Powered by AI         │ 🔄 📤 ⚙️        ││
│  │    Chatbot   │  Retrieval-Augmented Generation     │ Re   Up   Set   ││
│  └──────────────┴──────────────────────────────────────┴──────────────────┘│
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────┐  ┌────────────────────┐  │
│  │                                             │  │  UPLOAD SIDEBAR    │  │
│  │          CHAT WINDOW                        │  │ (When open)        │  │
│  │                                             │  │                    │  │
│  │  💬 Start a Conversation                   │  │ 📋 Upload Docs    │  │
│  │  Ask questions about your documents.       │  │                    │  │
│  │  The RAG system will search through your   │  │ [Drag & Drop Box] │  │
│  │  document database and provide accurate,   │  │ PDF or Markdown   │  │
│  │  cited answers.                            │  │                    │  │
│  │                                             │  │ 📝 Tips:          │  │
│  │                                             │  │ • Upload PDF/MD   │  │
│  │  ┌─────────────────────────────────────┐  │  │ • Auto indexed    │  │
│  │  │ You                                  │  │  │ • Ask questions   │  │
│  │  │                                      │  │  │ • Get citations   │  │
│  │  │ What are the main features?        │  │  │                    │  │
│  │  │ 14:32                               │  │  │ [Close Button]     │  │
│  │  └─────────────────────────────────────┘  │  │                    │  │
│  │                                             │  └────────────────────┘  │
│  │  ┌───────────────┐                         │                           │
│  │  │AI             │                         │                           │
│  │  │               │                         │                           │
│  │  │The main       │                         │                           │
│  │  │features are:  │                         │                           │
│  │  │1. RAG-powered │                         │                           │
│  │  │2. Multi-stage │                         │                           │
│  │  │3. Confidence  │                         │                           │
│  │  │               │                         │                           │
│  │  │Confidence: 82%│                         │                           │
│  │  │📚 Sources (3) │                         │                           │
│  │  │ • chunk_001   │                         │                           │
│  │  │ • chunk_005   │                         │                           │
│  │  │ • chunk_012   │                         │                           │
│  │  │14:32  📋 [📋] │                         │                           │
│  │  └───────────────┘                         │                           │
│  │                                             │                           │
│  │  ┌──────────────────────────────────────┐  │                           │
│  │  │You                              14:35│  │                           │
│  │  │Tell me more                          │  │                           │
│  │  └──────────────────────────────────────┘  │                           │
│  │                                             │                           │
│  │  ┌───────────────┐                         │                           │
│  │  │AI             │                         │                           │
│  │  │⏳ Generating... │                       │                           │
│  │  └───────────────┘                         │                           │
│  │                                             │                           │
│  ├─────────────────────────────────────────────┤                           │
│  │ 💬 Type your message... (Shift+Enter for new line)       [➤ Send]     │  │
│  └─────────────────────────────────────────────┘                           │
└─────────────────────────────────────────────────────────────────────────────┘


// ============================================================================
// COMPONENT BREAKDOWN
// ============================================================================

HEADER COMPONENT
├─ Title & Tagline
├─ Logo/Avatar
├─ Navigation Buttons
│  ├─ Upload (📤)
│  ├─ Reindex (🔄)
│  └─ Settings (⚙️) [Optional]
└─ Mobile Menu (☰)
   ├─ Reindex
   └─ Settings

MAIN CONTENT (Two-column layout)
├─ CHAT WINDOW (flex: 1)
│  ├─ Messages Container
│  │  ├─ Empty State (if no messages)
│  │  └─ MessageItem[] (repeating)
│  │     ├─ Avatar
│  │     ├─ Bubble (styled by message type)
│  │     ├─ Content
│  │     ├─ Confidence Score
│  │     ├─ Sources (expandable)
│  │     └─ Timestamp & Copy Button
│  │
│  ├─ Loading Indicator (if loading)
│  └─ Message Input Area
│     ├─ Textarea (auto-expanding)
│     ├─ Send Button
│     └─ Error Display (if error)
│
└─ UPLOAD SIDEBAR (width: 320px, conditional)
   ├─ Title
   ├─ FileUpload Component
   │  ├─ Drag & Drop Zone
   │  ├─ "Click to upload" text
   │  ├─ File input (hidden)
   │  └─ Upload Progress List
   │     ├─ File item (uploading)
   │     │  ├─ Progress bar
   │     │  └─ Percentage
   │     ├─ File item (success)
   │     │  ├─ ✓ Icon
   │     │  └─ Remove button
   │     └─ File item (error)
   │        ├─ ⚠ Icon
   │        ├─ Error message
   │        └─ Remove button
   ├─ Tips Box
   │  ├─ 📝 Title
   │  └─ Bulleted list
   └─ Close Button


// ============================================================================
// MESSAGE ITEM STRUCTURE (User Message)
// ============================================================================

User Message (right-aligned):
┌────────────────────────────────┐
│ You                       14:32 │
│                                │
│ What are the main features?    │
│                                │
│ [Copy] 14:32                   │
└────────────────────────────────┘


// ============================================================================
// MESSAGE ITEM STRUCTURE (Assistant Message)
// ============================================================================

Assistant Message (left-aligned):
┌────────────────────────────────────────────────────────┐
│ AI (blue circle)                                       │
│                                                        │
│ The main features include:                             │
│ 1. RAG-powered question answering                      │
│ 2. Multi-stage answer synthesis                        │
│ 3. Confidence scoring and attribution                  │
│ 4. Hybrid semantic + keyword search                    │
│ 5. Full chat history support                           │
│                                                        │
│ ┌──────────────────────────────────────────────────┐  │
│ │ 📊 Confidence: 82.3%                             │  │
│ │                                                  │  │
│ │ 📚 Sources (3)                                   │  │
│ │ • chunk_001_feature_overview                     │  │
│ │ • chunk_005_rag_architecture                     │  │
│ │ • chunk_012_scoring_system                       │  │
│ │ + 2 more                                         │  │
│ └──────────────────────────────────────────────────┘  │
│                                                        │
│ [Copy] 14:32                                           │
└────────────────────────────────────────────────────────┘


// ============================================================================
// LOADING STATE
// ============================================================================

┌────────────────────┐
│ AI (blue circle)   │
│                    │
│ ⏳ (spinning)       │
└────────────────────┘


// ============================================================================
// EMPTY STATE
// ============================================================================

        💬
   Start a Conversation
   
Ask questions about your documents.
The RAG system will search through your
document database and provide accurate,
cited answers.


// ============================================================================
// FILE UPLOAD INTERFACE
// ============================================================================

Upload Documents

┌─────────────────────────────────────────┐
│ /⬆\                                     │
│                                         │
│ Click to upload or drag and drop       │
│                                         │
│        PDF or Markdown files            │
└─────────────────────────────────────────┘

Upload Progress:
┌─────────────────────────────────────┐
│ ✓ document1.pdf                 100% │
│ (after upload)                      │
└─────────────────────────────────────┘

┌──────────────────────────────────────┐
│ document2.pdf                    45% │
│ ████████░░░░░░░░░░░░░░░░░░░░░░░░░  │
│ (during upload)                     │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│ ⚠ document3.pdf                      │
│ File too large (max 10MB)            │
│ (error)                              │
└──────────────────────────────────────┘

📝 Tips:
• Upload PDF or Markdown files
• Files are automatically indexed
• Use "Reindex" to rebuild the index
• Ask questions about your documents

[Close Button]


// ============================================================================
// RESPONSIVE DESIGN
// ============================================================================

DESKTOP (1024px+):
┌─────────────────────────────────────────────────────┐
│ HEADER                                              │
├──────────────────────────────────┬──────────────────┤
│ CHAT WINDOW                      │ UPLOAD SIDEBAR   │
│ (flex: 1)                        │ (w: 320px)       │
├──────────────────────────────────┴──────────────────┤
│ INPUT                                               │
└─────────────────────────────────────────────────────┘

TABLET (768px):
┌─────────────────────────────────┐
│ HEADER                          │
├─────────────────────────────────┤
│ CHAT WINDOW                     │
│ (full width, overlay sidebar)   │
├─────────────────────────────────┤
│ INPUT                           │
└─────────────────────────────────┘
(Sidebar overlays on click)

MOBILE (320px):
┌─────────────────┐
│ HEADER (compact)│
├─────────────────┤
│ CHAT (full)     │
├─────────────────┤
│ INPUT (full)    │
└─────────────────┘
(Sidebar swipe-in)


// ============================================================================
// COLOR SCHEME (Tailwind CSS)
// ============================================================================

Primary: Blue (#0EA5E9)
  - Header background: gradient from blue-600 to indigo-600
  - User messages: bg-blue-600 text-white
  - Buttons: bg-blue-600 hover:bg-blue-700
  - Links: text-blue-500

Secondary: Light gray
  - Assistant messages: bg-white border-gray-200
  - Input area: bg-white border-gray-300
  - Sidebar: bg-white border-gray-200

Accents:
  - Success: green-500 (checkmarks)
  - Error: red-500 (warnings)
  - Info: blue-50 (backgrounds)

Text:
  - Primary: gray-800
  - Secondary: gray-600
  - Muted: gray-500


// ============================================================================
// ANIMATIONS
// ============================================================================

Fade-in: Messages appear with opacity transition
Slide-up: Messages slide up from bottom
Hover: Buttons and interactive elements have hover effects
Loading: Spinning indicator during API calls
Smooth scroll: Auto-scroll to latest message


// ============================================================================
// KEYBOARD SHORTCUTS
// ============================================================================

Enter          → Send message
Shift+Enter    → New line in input
Escape         → Close sidebar (mobile)
Ctrl/Cmd+K     → Focus input
Ctrl/Cmd+L     → Clear chat (Ctrl+Shift+L)


// ============================================================================
// ACCESSIBILITY
// ============================================================================

✓ Semantic HTML (main, nav, section, article)
✓ ARIA labels on buttons and interactive elements
✓ Keyboard navigation support
✓ High contrast colors (WCAG AA compliant)
✓ Focus states on interactive elements
✓ Screen reader friendly button labels
✓ Proper heading hierarchy
✓ Alt text on icons


// ============================================================================
// COMPONENT TECHNOLOGIES
// ============================================================================

React 18.3      - UI framework
TypeScript      - Type safety
Tailwind CSS    - Styling
Lucide Icons    - SVG icons (50+ icons)
Axios           - HTTP client
Vite            - Build tool


// ============================================================================
// API RESPONSE DISPLAY
// ============================================================================

Response from backend:
{
  "answer_text": "The main features are...",
  "confidence_score": 0.823,
  "source_chunk_ids": ["chunk_001", "chunk_005", "chunk_012"],
  "top_chunks": [
    {
      "id": "chunk_001",
      "text": "Feature description...",
      "combined_score": 0.95
    }
  ]
}

Displayed as:
- Answer text in message bubble
- Confidence as percentage bar
- Sources as expandable list
- Each source shows score


// ============================================================================
// COMPLETE INTERACTION FLOW
// ============================================================================

1. User opens http://localhost:5173
   → Empty state shown
   → "Start a Conversation" message

2. User types question
   → Input enabled
   → Send button highlighted

3. User clicks Send or presses Enter
   → Input disabled (loading state)
   → Message appears on right (user)
   → Loading indicator appears on left

4. Backend processes question
   → RAG system retrieves chunks
   → Generates 5 answers
   → Selects top chunks
   → Scores responses

5. Response received
   → Assistant message appears on left
   → Confidence score displayed
   → Sources listed (expandable)
   → Loading indicator disappears
   → Input re-enabled

6. User can:
   → Ask follow-up questions
   → Upload new documents
   → Click Reindex to rebuild
   → Copy message text
   → View sources


// ============================================================================
// ERROR HANDLING DISPLAY
// ============================================================================

Network Error:
┌──────────────────────────────┐
│ ⚠ Failed to get response     │
│ Connection timeout. Check... │
│ [Retry]                      │
└──────────────────────────────┘

Backend Error:
┌──────────────────────────────┐
│ ⚠ RAG system not initialized │
│ Check server logs            │
└──────────────────────────────┘

Upload Error:
┌────────────────────────────────┐
│ ⚠ document.pdf                 │
│ File too large (max 10MB)      │
│ [Retry] [×]                    │
└────────────────────────────────┘


This wireframe shows the complete UI/UX of the RAG Chatbot frontend!
