"use client";

import { useEffect, useState } from "react";
import ChatWidget from "../components/ChatWidget";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Bill = {
  amount: number;
  period_start: string;
  period_end: string;
  breakdown: Record<string, number>;
};

export default function DashboardPage() {
  const [bill, setBill] = useState<Bill | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}/bills/1`)
      .then((res) => res.json())
      .then(setBill)
      .catch(() => setBill(null));
  }, []);

  return (
    <main className="min-h-screen bg-slate-50 p-8">
      <h1 className="text-2xl font-semibold mb-6">Your Bill & Usage</h1>

      <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow p-6">
          <h2 className="text-lg font-medium mb-2">Current Bill</h2>
          {bill ? (
            <>
              <p className="text-3xl font-bold">₹{bill.amount}</p>
              <p className="text-sm text-slate-500 mb-4">
                {bill.period_start} — {bill.period_end}
              </p>
              <ul className="text-sm space-y-1">
                {Object.entries(bill.breakdown).map(([key, value]) => (
                  <li key={key} className="flex justify-between">
                    <span className="capitalize">{key.replace("_", " ")}</span>
                    <span>₹{value}</span>
                  </li>
                ))}
              </ul>
            </>
          ) : (
            <p className="text-slate-400">Loading… (start the backend on :8000)</p>
          )}
        </div>

        <ChatWidget />
      </section>
    </main>
  );
}
