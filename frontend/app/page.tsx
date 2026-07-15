"use client";

import { useEffect, useState } from "react";
import ChatWidget from "../components/ChatWidget";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

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

  const totalCharges = bill
    ? Object.values(bill.breakdown).reduce((a, b) => a + b, 0)
    : 0;

  return (
    <main className="min-h-screen bg-slate-100">

      {/* Header */}
      <header className="border-b bg-white shadow-sm">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-8 py-6">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">
              Wallet & Bill AI Agent
            </h1>

            <p className="mt-1 text-sm text-slate-500">
              Understand your bill, compare plans, and save money using AI.
            </p>
          </div>

          <div className="rounded-full bg-green-100 px-4 py-2 text-sm font-medium text-green-700">
            ● Account Active
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-7xl p-8">

        <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">

          {/* Left Panel */}
          <div className="space-y-6">

            {/* Current Bill */}
            <div className="rounded-2xl bg-white p-6 shadow">

              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-lg font-semibold">
                  Current Bill
                </h2>

                <span className="rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-700">
                  Latest
                </span>
              </div>

              {bill ? (
                <>
                  <div className="mb-4">
                    <p className="text-5xl font-bold text-slate-900">
                      ₹{bill.amount}
                    </p>

                    <p className="mt-2 text-sm text-slate-500">
                      {bill.period_start} → {bill.period_end}
                    </p>
                  </div>

                  <div className="space-y-3">

                    {Object.entries(bill.breakdown).map(([key, value]) => (
                      <div
                        key={key}
                        className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2"
                      >
                        <span className="capitalize text-slate-700">
                          {key.replace("_", " ")}
                        </span>

                        <span className="font-semibold">
                          ₹{value}
                        </span>
                      </div>
                    ))}

                  </div>
                </>
              ) : (
                <div className="animate-pulse text-slate-400">
                  Loading bill...
                </div>
              )}
            </div>

            {/* Quick Stats */}

            <div className="grid grid-cols-2 gap-4">

              <div className="rounded-xl bg-white p-5 shadow">
                <p className="text-xs uppercase tracking-wide text-slate-500">
                  Total Charges
                </p>

                <p className="mt-2 text-2xl font-bold">
                  ₹{totalCharges}
                </p>
              </div>

              <div className="rounded-xl bg-white p-5 shadow">
                <p className="text-xs uppercase tracking-wide text-slate-500">
                  Bill Items
                </p>

                <p className="mt-2 text-2xl font-bold">
                  {bill ? Object.keys(bill.breakdown).length : "--"}
                </p>
              </div>

            </div>

            {/* AI Tips */}

            <div className="rounded-xl border border-blue-200 bg-blue-50 p-5">

              <h3 className="mb-2 font-semibold text-blue-900">
                💡 AI Suggestions
              </h3>

              <ul className="space-y-2 text-sm text-blue-800">
                <li>• Ask why your bill increased.</li>
                <li>• Compare your current plan.</li>
                <li>• Check if a cheaper plan suits you.</li>
                <li>• Understand each bill charge.</li>
              </ul>

            </div>

          </div>

          {/* Chat Panel */}

          <div className="lg:col-span-2">

            <div className="rounded-2xl bg-white p-4 shadow">

              <ChatWidget />

            </div>

          </div>

        </div>

      </div>

    </main>
  );
}
