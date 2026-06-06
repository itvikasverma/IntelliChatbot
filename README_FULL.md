# LangGraph Personal Data Chat Bot

A powerful multi-tool AI chatbot built with LangGraph, FastAPI, Next.js, and Groq that combines real-time web search, Wikipedia knowledge, personal document RAG, and intelligent memory management.

## ✨ Features

- **🤖 Multi-Tool AI Agent** - Intelligently chooses which tool to use based on queries
- **🔍 Real-Time Web Search** - DuckDuckGo and Google search with page scraping
- **📚 Wikipedia Integration** - Access encyclopedic information instantly
- **📄 Personal Document RAG** - Search through your own PDFs and documents
- **💭 Conversation Memory** - Thread-based memory for coherent multi-turn conversations
- **⚡ Streaming Responses** - Real-time tool execution indicators showing which tools are being called
- **🎨 Modern UI** - Beautiful Next.js frontend with real-time tool indicators
- **🟢 Live Tool Indicators** - See which tool is currently executing with pulsing dots and "calling" badges

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                       │
│  - React components with real-time tool indicators          │
│  - Server-sent events (SSE) streaming                       │
│  - Local storage for message/thread persistence             │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│           Next.js API Routes (Middleware)                   │
│  - /api/chat - Traditional request/response                 │
│  - /api/chat/stream - Streaming with tool indicators        │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│            Backend (FastAPI + LangGraph)                    │
│  ┌──────────────────────────────────────┐                   │
│  │  LangGraph ReAct Agent               │                   │
│  │  - Groq LLM (llama-3.3-70b)          │                   │
│  │  - Tool Router & Executor            │                   │
│  │  - Thread-based Memory               │                   │
│  └──────────────────────────────────────┘                   │
│              │                                               │
│  ┌───────────┼──────────────────────────┐                   │
│  │           │                          │                   │
│  ▼           ▼                          ▼                   │
│ Tools    RAG Engine              Message History            │
│ ├─ DuckDuckGo      ┌──────────────┐    │                    │
│ ├─ Google          │ Qdrant       │    │                    │
│ ├─ Wikipedia       │ Vector DB    │    │                    │
│ └─ Personal Data   └──────────────┘    │                    │
└──────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker & Docker Compose (for Qdrant)
- Groq API Key ([get one here](https://console.groq.com))

### 1. Clone & Setup Python Environment

```bash
# Clone repository
git clone <your-repo>
cd chatbot

# Create virtual environment
python -m venv .venv

# Activate it
# On Windows:
.venv\Scripts\activate
# On Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file in project root:

```env
# Groq API (required)
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# Qdrant Vector Database
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=
QDRANT_COLLECTION=personal_memory
QDRANT_TIMEOUT=60

# Embedding Model
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5

# Chatbot System Prompt (optional)
CHATBOT_SYSTEM_PROMPT=You are a helpful assistant. Use tools when they improve factual accuracy. Prefer the personal data RAG tool for personal or user-specific facts.
```

### 3. Start Services

```bash
# Terminal 1: Start Qdrant (vector database)
docker-compose up -d

# Terminal 2: Start Python backend
uvicorn chatbot.api:app --reload

# Terminal 3: Start Next.js frontend
cd web
npm install
npm run dev
```

The app will be available at: `http://localhost:3000`

### 4. Ingest Your Documents

To add personal data (PDFs, text files):

```bash
# Ingest a specific file
python -m chatbot.ingest data/personal-data/your_document.pdf

# Or ingest entire directory
python -m chatbot.ingest data/personal-data/
```

Expected output:
```
Ingested 42 personal data chunks.
```

## 📋 Available Tools

### 1. **DuckDuckGo Search** 🔍
- Quick web searches
- Good for recent news and general queries
- Fast and lightweight

### 2. **Google Scraper** 🌐
- Searches Google and scrapes top results
- More comprehensive than DuckDuckGo
- Returns actual page content

### 3. **Wikipedia** 📚
- Encyclopedic information
- Background knowledge and definitions
- Top 3 results with content

### 4. **Personal Data RAG** 📄
- Searches your ingested documents
- Vector-based semantic search
- Perfect for resumes, notes, PDFs

## 🎯 Real-Time Tool Indicators

When asking a question, watch the **Tools panel** on the left sidebar:

```
Tools
🟢 DuckDuckGo              [inactive - gray dot]
🟢 Google scrape [calling] [active - green dot + badge]
🟢 Wikipedia               [inactive - gray dot]
🟢 Personal data RAG       [inactive - gray dot]
```

Visual feedback:
- ⚪ **Gray dot** = Not executing
- 🟢 **Green pulsing dot** = Currently executing
- 🟢 **"calling" badge** = Tool actively running
- 🟢 **Green background** = Active tool highlighted

## 💬 Usage Examples

### Search Web
```
"What are the latest developments in AI?"
→ Tool: google_scraper
```

### Query Wikipedia
```
"Tell me about machine learning"
→ Tool: wikipedia_search
```

### Personal Data
```
"What are my technical skills?"
→ Tool: personal_data_rag_search
```

### Conversational
```
"Hi, how are you?"
→ No tools (simple greeting)
```

## 🔧 Project Structure

```
chatbot/
├── chatbot/
│   ├── __init__.py
│   ├── agent.py          # LangGraph agent & streaming
│   ├── api.py            # FastAPI endpoints
│   ├── cli.py            # Command-line interface
│   ├── config.py         # Configuration
│   ├── ingest.py         # CLI for data ingestion
│   ├── rag.py            # RAG engine (Qdrant)
│   └── tools.py          # Tool definitions
├── web/
│   ├── app/
│   │   ├── page.tsx      # Main chat UI
│   │   ├── layout.tsx    # Layout
│   │   ├── globals.css   # Styles
│   │   └── api/
│   │       └── chat/
│   │           ├── route.ts      # Standard chat endpoint
│   │           └── stream/
│   │               └── route.ts  # Streaming endpoint
│   ├── next.config.ts
│   ├── tsconfig.json
│   └── package.json
├── data/
│   ├── docs/             # Public documents
│   └── personal-data/    # Your documents (PDFs, etc)
├── docker-compose.yml    # Qdrant setup
├── requirements.txt      # Python dependencies
└── README.md
```

## 🛠️ Configuration

### Groq Models

Available models (set `GROQ_MODEL`):
- `llama-3.3-70b-versatile` (default) - Excellent for general tasks
- `mixtral-8x7b-32768` - Good for reasoning
- `gemma-7b-it` - Lightweight

### Embedding Model

Set `EMBEDDING_MODEL` for RAG:
- `BAAI/bge-small-en-v1.5` (default) - Fast, small
- `BAAI/bge-base-en-v1.5` - Larger, more accurate
- `BAAI/bge-large-en-v1.5` - Largest, best quality

## 🔄 API Endpoints

### Standard Chat
```bash
POST /chat
Content-Type: application/json

{
  "message": "What are my technical skills?",
  "thread_id": "thread-abc123"
}

Response:
{
  "answer": "Based on your resume...",
  "thread_id": "thread-abc123",
  "tools_used": ["personal_data_rag_search"]
}
```

### Streaming Chat
```bash
POST /api/chat/stream
Content-Type: application/json

{
  "message": "Search for Python tutorials",
  "thread_id": "thread-abc123"
}

Response: Server-Sent Events (SSE)
data: {"type":"tool_start","tool":"google_scraper",...}
data: {"type":"tool_end","tool":"google_scraper",...}
data: {"type":"response","answer":"...","tools_used":[...]}
```

## 🧠 Memory Management

- **Thread-based**: Each conversation has a unique thread_id
- **Short-term context**: Maintains message history within thread
- **Persistent**: Threads stored in Qdrant checkpointer
- **Local storage**: Browser stores current thread_id and messages

## 🐛 Troubleshooting

### Qdrant Connection Error
```
ERROR: Personal data RAG is not ready
```
**Fix**: Make sure Docker is running
```bash
docker ps  # Should show qdrant container
docker-compose up -d  # Start if not running
```

### Tool Not Calling
- Check browser console (F12) for `[STREAM]` logs
- Ensure backend is running: `http://localhost:8000/health`
- Check for network errors in DevTools Network tab

### No Documents in RAG
```
No matching personal data memory found.
```
**Fix**: Ingest documents first
```bash
python -m chatbot.ingest data/personal-data/
```

### Version Mismatch Warning
```
Qdrant client version X is incompatible with server version Y
```
This is safe to ignore - the system still works. To fix:
```bash
pip install qdrant-client==1.15.4
```

## 📈 Performance Tips

1. **Chunk Size**: Adjust in `rag.py` for optimal RAG performance
2. **Embedding Model**: Larger models are slower but more accurate
3. **API Timeout**: Increase `QDRANT_TIMEOUT` for large queries
4. **Temperature**: Lower (0.0-0.3) for factual, higher (0.7+) for creative

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- Built with [LangGraph](https://langchain-ai.github.io/langgraph/)
- LLM powered by [Groq](https://groq.com)
- Vector database [Qdrant](https://qdrant.tech)
- Frontend with [Next.js](https://nextjs.org) and [React](https://react.dev)
- Icons by [Lucide](https://lucide.dev)

## 📞 Support

For issues and questions:
1. Check the Troubleshooting section
2. Review terminal/console logs
3. Open an issue on GitHub

---

**Happy Chatting! 🚀**
