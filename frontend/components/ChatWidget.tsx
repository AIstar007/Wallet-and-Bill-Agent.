"use client";

import { useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Message = { role: "user" | "assistant"; text: string };

export default function ChatWidget() {
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", text: "Ask me why your bill changed, or whether a different plan would save you money." },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function sendMessage() {
    if (!input.trim()) return;
    const userMsg: Message = { role: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMsg.text }),
      });
      const data = await res.json();
      setMessages((prev) => [...prev, { role: "assistant", text: data.answer }]);
    } catch {
      setMessages((prev) => [...prev, { role: "assistant", text: "Backend not reachable — is it running on :8000?" }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="bg-white rounded-xl shadow p-6 flex flex-col h-96">
      <h2 className="text-lg font-medium mb-2">Bill & Plan Agent</h2>
      <div className="flex-1 overflow-y-auto space-y-2 mb-3">
        {messages.map((m, i) => (
          <div key={i} className={m.role === "user" ? "text-right" : "text-left"}>
            <span
              className={`inline-block px-3 py-2 rounded-lg text-sm ${
                m.role === "user" ? "bg-blue-600 text-white" : "bg-slate-100 text-slate-800"
              }`}
            >
              {m.text}
            </span>
          </div>
        ))}
        {loading && <p className="text-xs text-slate-400">Thinking…</p>}
      </div>
      <div className="flex gap-2">
        <input
          className="flex-1 border rounded-lg px-3 py-2 text-sm"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          placeholder="Why is my bill higher this month?"
        />
        <button onClick={sendMessage} className="bg-blue-600 text-white rounded-lg px-4 py-2 text-sm">
          Send
        </button>
      </div>
    </div>
  );
}
