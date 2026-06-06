from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import json

from chatbot.agent import chat, stream_chat


app = FastAPI(title="LangGraph Multi-Tool Chatbot")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    thread_id: str = "default"


class ChatResponse(BaseModel):
    answer: str
    thread_id: str
    tools_used: list[str] = Field(default_factory=list, description="List of tools called to generate this response")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest) -> ChatResponse:
    answer, tools_used = chat(request.message, thread_id=request.thread_id)
    return ChatResponse(answer=answer, thread_id=request.thread_id, tools_used=tools_used)


@app.post("/chat/stream")
def chat_stream_endpoint(request: ChatRequest):
    """Stream tool calls and final response in real-time."""
    def event_generator():
        for event in stream_chat(request.message, thread_id=request.thread_id):
            print(f"[API] Sending event: {event['type']} - {event.get('tool', '')}")
            yield f"data: {json.dumps(event)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
