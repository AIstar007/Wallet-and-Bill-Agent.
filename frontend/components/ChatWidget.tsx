"use client";

import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Message = {
  role: "user" | "assistant";
  text: string;
};

export default function ChatWidget() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      text: "👋 Hi! Ask me why your bill changed, compare plans, or explain any charge on your bill.",
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

  async function sendMessage() {
    if (!input.trim()) return;

    const userMsg: Message = {
      role: "user",
      text: input.trim(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: userMsg.text,
        }),
      });

      const data = await res.json();

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: data.answer,
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: "❌ Backend not reachable. Is the FastAPI server running on port 8000?",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex h-96 flex-col rounded-xl bg-white p-6 shadow">

      <h2 className="mb-4 text-lg font-semibold">
        Bill & Plan Agent
      </h2>

      <div className="flex-1 overflow-y-auto space-y-4">

        {messages.map((m, i) => (
          <div
            key={i}
            className={`flex ${
              m.role === "user"
                ? "justify-end"
                : "justify-start"
            }`}
          >
            <div
              className={`w-fit max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-7 shadow-sm ${
                m.role === "user"
                  ? "bg-blue-600 text-white"
                  : "border border-slate-200 bg-white text-slate-800"
              }`}
            >
              {m.role === "assistant" ? (
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    h1: ({ children }) => (
                      <h1 className="mb-2 text-lg font-bold">
                        {children}
                      </h1>
                    ),

                    h2: ({ children }) => (
                      <h2 className="mb-2 text-base font-semibold">
                        {children}
                      </h2>
                    ),

                    p: ({ children }) => (
                      <p className="mb-2 last:mb-0">
                        {children}
                      </p>
                    ),

                    ul: ({ children }) => (
                      <ul className="mb-2 list-disc pl-6">
                        {children}
                      </ul>
                    ),

                    ol: ({ children }) => (
                      <ol className="mb-2 list-decimal pl-6">
                        {children}
                      </ol>
                    ),

                    li: ({ children }) => (
                      <li className="mb-1">
                        {children}
                      </li>
                    ),

                    strong: ({ children }) => (
                      <strong className="font-semibold">
                        {children}
                      </strong>
                    ),

                    table: ({ children }) => (
                      <table className="my-3 w-full border-collapse border border-slate-300">
                        {children}
                      </table>
                    ),

                    th: ({ children }) => (
                      <th className="border border-slate-300 bg-slate-100 px-3 py-2 text-left">
                        {children}
                      </th>
                    ),

                    td: ({ children }) => (
                      <td className="border border-slate-300 px-3 py-2">
                        {children}
                      </td>
                    ),

                    code(props) {
                      const { children, className } = props;

                      return (
                        <code
                          className={`rounded bg-slate-100 px-1 py-0.5 font-mono text-red-600 ${className ?? ""}`}
                        >
                          {children}
                        </code>
                      );
                    },
                  }}
                >
                  {m.text}
                </ReactMarkdown>
              ) : (
                m.text
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-500 shadow-sm">
              Thinking...
            </div>
          </div>
        )}

        <div ref={bottomRef} />

      </div>

      <div className="mt-4 flex gap-2">

        <textarea
          rows={1}
          className="flex-1 resize-none rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Why is my bill higher this month?"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              sendMessage();
            }
          }}
        />

        <button
          onClick={sendMessage}
          disabled={loading}
          className="rounded-lg bg-blue-600 px-5 py-2 text-sm text-white transition hover:bg-blue-700 disabled:opacity-50"
        >
          Send
        </button>

      </div>

    </div>
  );
}
