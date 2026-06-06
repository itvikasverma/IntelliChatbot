import { NextRequest, NextResponse } from "next/server";

type BackendChatResponse = {
  answer: string;
  thread_id: string;
};

export async function POST(request: NextRequest) {
  const body = await request.json();
  const apiUrl = process.env.CHATBOT_API_URL ?? "http://127.0.0.1:8000";

  const response = await fetch(`${apiUrl}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const detail = await response.text();
    return NextResponse.json(
      { error: detail || "Backend chat request failed" },
      { status: response.status },
    );
  }

  const data = (await response.json()) as BackendChatResponse;
  return NextResponse.json(data);
}
