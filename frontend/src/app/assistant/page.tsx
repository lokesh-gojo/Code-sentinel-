"use client";

import React, { useState } from "react";
import { api } from "@/lib/api";
import { BotMessageSquare, Send, Sparkles, Terminal, Cpu } from "lucide-react";

interface Message {
  sender: "user" | "assistant";
  text: string;
  provider?: string;
}

export default function AssistantPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      sender: "assistant",
      text: "Hello! I am Code Sentinel AI, your repository-aware productivity assistant. Ask me to explain architecture, audit security vulnerabilities, or investigate root causes.",
    },
  ]);
  const [input, setInput] = useState("");
  const [provider, setProvider] = useState<"auto" | "gemini" | "ollama">("auto");
  const [loading, setLoading] = useState(false);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const query = input;
    setInput("");
    setMessages((prev) => [...prev, { sender: "user", text: query }]);
    setLoading(true);

    try {
      const res = await api.chatAssistant(query, "default", provider);
      setMessages((prev) => [
        ...prev,
        { sender: "assistant", text: res.reply, provider: res.provider_used },
      ]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        { sender: "assistant", text: `Assistant error: ${err.message}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 h-[calc(100vh-80px)] flex flex-col">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-4 pb-4 border-b border-gray-800">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <BotMessageSquare className="w-5 h-5 text-indigo-400" />
            Developer Productivity Assistant
          </h1>
          <p className="text-xs text-gray-400">
            Connected to repository dependency graphs, static findings, and project memory.
          </p>
        </div>

        {/* Multi-LLM Provider Selector */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400 font-mono">Inference Engine:</span>
          <select
            value={provider}
            onChange={(e: any) => setProvider(e.target.value)}
            className="bg-gray-900 border border-gray-700 text-gray-200 text-xs rounded-lg px-2.5 py-1.5 font-mono"
          >
            <option value="auto">Auto (Gemini Cloud ➔ Ollama Offline)</option>
            <option value="gemini">Google Gemini 2.5 Flash</option>
            <option value="ollama">Ollama (Local Offline)</option>
          </select>
        </div>
      </div>

      {/* Messages Feed */}
      <div className="flex-1 overflow-y-auto space-y-4 p-4 rounded-2xl bg-gray-900/60 border border-gray-800">
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`flex ${m.sender === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] p-4 rounded-2xl text-xs leading-relaxed ${
                m.sender === "user"
                  ? "bg-indigo-600 text-white rounded-br-none"
                  : "bg-gray-950 text-gray-200 border border-gray-800 rounded-bl-none shadow-md"
              }`}
            >
              {m.sender === "assistant" && (
                <div className="flex items-center justify-between gap-2 mb-1.5 text-[10px] text-indigo-400 font-mono font-semibold">
                  <span className="flex items-center gap-1">
                    <Sparkles className="w-3 h-3" /> Code Sentinel AI
                  </span>
                  {m.provider && (
                    <span className="uppercase text-gray-500 bg-gray-900 px-1.5 py-0.5 rounded">
                      {m.provider}
                    </span>
                  )}
                </div>
              )}
              <div className="whitespace-pre-wrap">{m.text}</div>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="p-3 rounded-2xl bg-gray-950 text-gray-400 border border-gray-800 text-xs flex items-center gap-2">
              <Cpu className="w-4 h-4 animate-spin text-indigo-400" />
              Reasoning over repository evidence...
            </div>
          </div>
        )}
      </div>

      {/* Suggested Quick Prompts */}
      <div className="py-3 flex flex-wrap gap-2 text-[11px]">
        {[
          "Explain the architecture of this project",
          "Find all security vulnerabilities",
          "Why might a zero division occur in math utils?",
          "Show project conventions and rules",
        ].map((prompt, idx) => (
          <button
            key={idx}
            onClick={() => setInput(prompt)}
            className="px-2.5 py-1 rounded-lg bg-gray-800/80 hover:bg-gray-700 text-gray-300 border border-gray-700/60 transition"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Input Field */}
      <form onSubmit={handleSend} className="flex items-center gap-3 mt-1">
        <input
          type="text"
          placeholder="Ask Code Sentinel about bugs, security, or architecture..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="flex-1 bg-gray-900 border border-gray-700 text-white text-xs rounded-xl p-3 focus:outline-none focus:border-indigo-500 font-mono"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="p-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl transition shadow-lg shadow-indigo-600/20 disabled:opacity-50"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
}
