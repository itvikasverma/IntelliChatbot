"use client";

import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import {
  Bot,
  Brain,
  CheckCircle2,
  Loader2,
  MessageSquarePlus,
  Search,
  Send,
  Sparkles,
  Trash2,
  User,
} from "lucide-react";

type Role = "assistant" | "user";

type ChatMessage = {
  id: string;
  role: Role;
  content: string;
  createdAt: string;
  toolsUsed?: string[];
};

const THREAD_KEY = "personal-data-tools-chat-thread";
const MESSAGES_KEY = "personal-data-tools-chat-messages";

function makeId(prefix: string) {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return `${prefix}-${crypto.randomUUID()}`;
  }
  return `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function makeThreadId() {
  return makeId("thread");
}

function shortThread(threadId: string) {
  return threadId.replace("thread-", "").slice(0, 8);
}

export default function Home() {
  const [mounted, setMounted] = useState(false);
  const [threadId, setThreadId] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState("");
  const [activeTools, setActiveTools] = useState<Record<string, boolean>>({});
  const scrollRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const storedThread = window.localStorage.getItem(THREAD_KEY);
    const storedMessages = window.localStorage.getItem(MESSAGES_KEY);
    const nextThread = storedThread || makeThreadId();

    setThreadId(nextThread);
    window.localStorage.setItem(THREAD_KEY, nextThread);

    if (storedMessages) {
      try {
        setMessages(JSON.parse(storedMessages) as ChatMessage[]);
      } catch {
        window.localStorage.removeItem(MESSAGES_KEY);
      }
    }
    
    setMounted(true);
  }, []);

  useEffect(() => {
    if (messages.length > 0) {
      window.localStorage.setItem(MESSAGES_KEY, JSON.stringify(messages));
    }
  }, [messages]);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, isSending]);

  const memoryStatus = useMemo(() => {
    if (!threadId) return "Starting memory";
    return `Memory active · ${shortThread(threadId)}`;
  }, [threadId]);

  async function sendMessage(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const content = input.trim();
    if (!content || isSending || !threadId) return;

    const userMessage: ChatMessage = {
      id: makeId("user"),
      role: "user",
      content,
      createdAt: new Date().toISOString(),
    };

    setMessages((current) => [...current, userMessage]);
    setInput("");
    setError("");
    setIsSending(true);
    setActiveTools({});

    console.log("[STREAM] Starting stream fetch...");

    try {
      const response = await fetch("/api/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: content, thread_id: threadId }),
      });

      if (!response.ok) {
        throw new Error("Chat request failed");
      }

      console.log("[STREAM] Response OK, reading body...");

      if (!response.body) {
        throw new Error("No response body");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let toolsUsedFinal: string[] = [];

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const text = decoder.decode(value);
        console.log("[STREAM] Raw text:", text);
        const lines = text.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const eventStr = line.slice(6);
              console.log("[STREAM] Parsing event:", eventStr);
              const event = JSON.parse(eventStr);
              console.log("[STREAM] Event parsed:", event);

              if (event.type === "tool_start") {
                console.log(`[STREAM] Tool started: ${event.tool}`);
                setActiveTools((prev) => {
                  const next = { ...prev, [event.tool]: true };
                  console.log("[STREAM] activeTools updated to:", next);
                  return next;
                });
              } else if (event.type === "tool_end") {
                console.log(`[STREAM] Tool ended: ${event.tool}`);
                setActiveTools((prev) => {
                  const next = { ...prev };
                  delete next[event.tool];
                  console.log("[STREAM] activeTools updated to:", next);
                  return next;
                });
              } else if (event.type === "response") {
                console.log("[STREAM] Response received:", event);
                toolsUsedFinal = event.tools_used || [];
                setMessages((current) => [
                  ...current,
                  {
                    id: makeId("assistant"),
                    role: "assistant",
                    content: event.answer,
                    createdAt: new Date().toISOString(),
                    toolsUsed: toolsUsedFinal,
                  },
                ]);
              }
            } catch (err) {
              console.error("[STREAM] Parse error:", err, "Line:", line);
            }
          }
        }
      }
    } catch (err) {
      console.error("[STREAM] Error:", err);
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setIsSending(false);
      setActiveTools({});
    }
  }

  function newChat() {
    const nextThread = makeThreadId();
    setThreadId(nextThread);
    setMessages([]);
    setError("");
    window.localStorage.setItem(THREAD_KEY, nextThread);
    window.localStorage.removeItem(MESSAGES_KEY);
  }

  if (!mounted) {
    return <main className="app-shell" />;
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">
            <Bot size={22} aria-hidden />
          </div>
          <div>
            <p className="eyebrow">LangGraph</p>
            <h1>Personal Data Chat</h1>
          </div>
        </div>

        <button className="primary-action" type="button" onClick={newChat}>
          <MessageSquarePlus size={18} aria-hidden />
          New chat
        </button>

        <section className="status-panel" aria-label="Memory status">
          <div className="status-row">
            <Brain size={18} aria-hidden />
            <span>{memoryStatus}</span>
          </div>
          <div className="status-row">
            <CheckCircle2 size={18} aria-hidden />
            <span>Short-term context via thread</span>
          </div>
        </section>

        <section className="tool-panel" aria-label="Available tools">
          <p className="panel-title">Tools</p>
          <div className="tool-list">
            <span className={activeTools["duckduckgo_search"] ? "tool-active" : ""}>
              <div className="tool-indicator" />
              <Search size={15} aria-hidden /> DuckDuckGo
              {activeTools["duckduckgo_search"] && <span className="tool-badge-calling">calling</span>}
            </span>
            <span className={activeTools["google_scraper"] ? "tool-active" : ""}>
              <div className="tool-indicator" />
              <Search size={15} aria-hidden /> Google scrape
              {activeTools["google_scraper"] && <span className="tool-badge-calling">calling</span>}
            </span>
            <span className={activeTools["wikipedia_search"] ? "tool-active" : ""}>
              <div className="tool-indicator" />
              <Sparkles size={15} aria-hidden /> Wikipedia
              {activeTools["wikipedia_search"] && <span className="tool-badge-calling">calling</span>}
            </span>
            <span className={activeTools["personal_data_rag_search"] ? "tool-active" : ""}>
              <div className="tool-indicator" />
              <Brain size={15} aria-hidden /> Personal data RAG
              {activeTools["personal_data_rag_search"] && <span className="tool-badge-calling">calling</span>}
            </span>
          </div>
        </section>
      </aside>

      <section className="chat-area" aria-label="Chat">
        <header className="chat-header">
          <div>
            <p className="eyebrow">Groq powered assistant</p>
            <h2>Ask with tools and memory</h2>
          </div>
          <button className="icon-button" type="button" onClick={newChat} aria-label="Clear chat">
            <Trash2 size={18} aria-hidden />
          </button>
        </header>

        <div className="messages">
          {messages.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">
                <Sparkles size={28} aria-hidden />
              </div>
              <h3>Start a conversation</h3>
              <p>
                Ask about current web facts, Wikipedia topics, scraped pages, or your personal data memory.
              </p>
            </div>
          ) : (
            messages.map((message) => (
              <article className={`message ${message.role}`} key={message.id}>
                <div className="avatar" aria-hidden>
                  {message.role === "assistant" ? <Bot size={18} /> : <User size={18} />}
                </div>
                <div className="bubble">
                  <p>{message.content}</p>
                  {message.role === "assistant" && (
                    <div className="tools-used">
                      <span className="tools-label">Tools used:</span>
                      {message.toolsUsed && message.toolsUsed.length > 0 ? (
                        message.toolsUsed.map((tool, index) => (
                          <span key={index} className="tool-badge">
                            {tool}
                          </span>
                        ))
                      ) : (
                        <span className="tool-badge tool-none">No tools</span>
                      )}
                    </div>
                  )}
                </div>
              </article>
            ))
          )}

          {isSending ? (
            <article className="message assistant">
              <div className="avatar" aria-hidden>
                <Bot size={18} />
              </div>
              <div className="bubble typing">
                <Loader2 size={17} aria-hidden />
                Thinking with tools...
              </div>
            </article>
          ) : null}

          <div ref={scrollRef} />
        </div>

        {error ? <div className="error-banner">{error}</div> : null}

        <form className="composer" onSubmit={sendMessage}>
          <textarea
            aria-label="Message"
            placeholder="Ask anything..."
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                event.currentTarget.form?.requestSubmit();
              }
            }}
            rows={1}
          />
          <button className="send-button" type="submit" disabled={!input.trim() || isSending}>
            {isSending ? <Loader2 size={18} aria-hidden /> : <Send size={18} aria-hidden />}
            Send
          </button>
        </form>
      </section>
    </main>
  );
}
