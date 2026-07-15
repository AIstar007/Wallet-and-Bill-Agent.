"use client";

import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Message = {
  role: "user" | "assistant";
  text: string;
  timestamp?: string;
};

const suggestions = [
  "Why is my bill higher?",
  "Recommend a cheaper plan",
  "Compare available plans",
  "Explain my bill",
];

export default function ChatWidget() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      text: "👋 Hi! Ask me why your bill changed, compare plans, or explain any charge on your bill.",
      timestamp: new Date().toLocaleTimeString([], {hour:"2-digit",minute:"2-digit"})
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({behavior:"smooth"});
  }, [messages, loading]);

  useEffect(() => {
    if (!textareaRef.current) return;
    textareaRef.current.style.height = "0px";
    textareaRef.current.style.height = textareaRef.current.scrollHeight + "px";
  }, [input]);

  function copyMessage(text:string){
    navigator.clipboard.writeText(text);
  }

  async function sendMessage() {
    if (!input.trim() || loading) return;

    const userMsg: Message = {
      role:"user",
      text:input.trim(),
      timestamp:new Date().toLocaleTimeString([], {hour:"2-digit",minute:"2-digit"})
    };

    setMessages(prev=>[...prev,userMsg]);
    setInput("");
    setLoading(true);

    try{
      const res=await fetch(`${API_BASE}/chat`,{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({message:userMsg.text})
      });

      const data=await res.json();

      setMessages(prev=>[
        ...prev,
        {
          role:"assistant",
          text:data.answer,
          timestamp:new Date().toLocaleTimeString([], {hour:"2-digit",minute:"2-digit"})
        }
      ]);
    }catch{
      setMessages(prev=>[
        ...prev,
        {
          role:"assistant",
          text:"❌ Backend not reachable.",
          timestamp:new Date().toLocaleTimeString([], {hour:"2-digit",minute:"2-digit"})
        }
      ]);
    }finally{
      setLoading(false);
    }
  }

  return (
    <div className="flex h-[32rem] flex-col rounded-xl bg-white p-6 shadow">
      <h2 className="mb-4 text-lg font-semibold">Bill & Plan Agent</h2>

      <div className="mb-4 flex flex-wrap gap-2">
        {suggestions.map((s)=>(
          <button key={s}
            onClick={()=>setInput(s)}
            className="rounded-full border px-3 py-1 text-xs hover:bg-slate-100">
            {s}
          </button>
        ))}
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto">
        {messages.map((m,i)=>(
          <div key={i} className={`flex ${m.role==="user"?"justify-end":"justify-start"}`}>
            <div className="group relative">
              {m.role==="assistant" && (
                <button
                  onClick={()=>copyMessage(m.text)}
                  className="absolute -right-2 -top-2 hidden rounded bg-white px-2 py-1 text-xs shadow group-hover:block">
                  📋
                </button>
              )}

              <div className={`w-fit max-w-[85%] rounded-2xl px-4 py-3 shadow-sm ${
                m.role==="user"
                ?"bg-blue-600 text-white"
                :"border border-slate-200 bg-white text-slate-800"
              }`}>
                {m.role==="assistant" ? (
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}>
                    {m.text}
                  </ReactMarkdown>
                ) : (
                  <p>{m.text}</p>
                )}
                <div className="mt-2 text-right text-[10px] opacity-60">
                  {m.timestamp}
                </div>
              </div>
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="rounded-2xl border bg-white px-4 py-3 shadow-sm">
              <div className="flex gap-1">
                <span className="h-2 w-2 animate-bounce rounded-full bg-slate-500"/>
                <span className="h-2 w-2 animate-bounce rounded-full bg-slate-500" style={{animationDelay:"150ms"}}/>
                <span className="h-2 w-2 animate-bounce rounded-full bg-slate-500" style={{animationDelay:"300ms"}}/>
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef}/>
      </div>

      <div className="mt-4 flex gap-2">
        <textarea
          ref={textareaRef}
          rows={1}
          value={input}
          onChange={(e)=>setInput(e.target.value)}
          onKeyDown={(e)=>{
            if(e.key==="Enter" && !e.shiftKey){
              e.preventDefault();
              sendMessage();
            }
          }}
          placeholder="Why is my bill higher this month?"
          className="flex-1 resize-none rounded-xl border px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          disabled={loading}
          onClick={sendMessage}
          className="rounded-xl bg-blue-600 px-5 py-3 text-white disabled:opacity-50">
          {loading ? "..." : "Send"}
        </button>
      </div>
    </div>
  );
}
