# LangGraph Multi-Tool Chatbot

Python chatbot using LangGraph tool calling with Groq:

- DuckDuckGo web search
- Wikipedia lookup
- Google result scraper
- Web page scraper
- Personal data RAG backed by Qdrant

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and add `GROQ_API_KEY`.

Start Qdrant locally:

```powershell
docker compose up -d
```

## Add RAG Data

Put personal facts in `data/personal-data/` as `.pdf`, `.txt`, or `.md` files. Put knowledge documents in `data/docs/` as `.pdf`, `.txt`, or `.md` files.

Ingest both folders:

```powershell
python -m chatbot.ingest data/personal-data
python -m chatbot.ingest data/docs
```

You can also ingest one file:

```powershell
python -m chatbot.ingest data/personal-data/about_me.md
python -m chatbot.ingest data/docs/product_manual.pdf
```

## Run CLI Chat

```powershell
python -m chatbot.cli
```

## Run API

```powershell
uvicorn chatbot.api:app --reload --port 8000
```

Then call:

```powershell
Invoke-RestMethod -Method Post http://localhost:8000/chat `
  -ContentType "application/json" `
  -Body '{"message":"What do you know about my preferences?","thread_id":"demo"}'
```

## Run Next.js UI

```powershell
cd web
npm install
Copy-Item .env.local.example .env.local
npm run dev
```

Open `http://localhost:3000`.

The UI keeps a browser session `thread_id` in local storage. That `thread_id` is sent to the FastAPI backend on every message, so LangGraph short-term memory continues across messages and page refreshes. Use **New chat** to reset the thread.

## Notes

The agent is built with `langgraph.prebuilt.create_react_agent`, which handles the repeated model/tool loop until the model produces a final answer. The Qdrant personal data tool returns private context snippets to the model and is best for user-specific information.

Chat responses use Groq through `langchain-groq`. Personal data RAG embeddings use local FastEmbed by default, so RAG does not require an OpenAI key.
