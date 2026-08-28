import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { Send, Bot, User, Sparkles, RefreshCw } from "lucide-react";

export default function App() {
  const [messages, setMessages] = useState([
    {
      sender: "agent",
      text: "👋 Hello! Welcome to TechGear Support. How can I assist you with your orders today?",
      time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
    }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(() => "user_" + Math.random().toString(36).substring(2, 9));
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    const currentTime = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

    setMessages((prev) => [...prev, { sender: "user", text: userMessage, time: currentTime }]);
    setInput("");
    setLoading(true);

    try {
      const response = await axios.post("http://localhost:8000/chat", {
        message: userMessage,
        session_id: sessionId,
      });

      setMessages((prev) => [
        ...prev,
        {
          sender: "agent",
          text: response.data.response,
          time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
        }
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          sender: "agent",
          text: "⚠️ Error: Unable to connect to the AI backend. Please check if the Docker container is running.",
          time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const resetSession = () => {
    const newId = "user_" + Math.random().toString(36).substring(2, 9);
    setSessionId(newId);
    setMessages([
      {
        sender: "agent",
        text: "Session reset. How can I assist you with your orders?",
        time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
      }
    ]);
  };

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4 font-sans antialiased text-slate-100">
      <div className="w-full max-w-2xl h-[85vh] bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl flex flex-col overflow-hidden backdrop-blur-lg">
        
        {/* Header */}
        <header className="px-6 py-4 bg-slate-900/80 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-blue-600/20 text-blue-400 rounded-xl border border-blue-500/30 flex items-center justify-center">
              <Bot className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-base font-semibold tracking-wide">TechGear Support</h1>
                <span className="flex h-2 w-2 relative">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
              </div>
              <p className="text-xs text-slate-400">Autonomous AI Assistant</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs font-mono bg-slate-800 text-slate-300 px-2.5 py-1 rounded-md border border-slate-700">
              {sessionId}
            </span>
            <button
              onClick={resetSession}
              title="Reset Chat Session"
              className="p-2 text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors border border-slate-700"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </header>

        {/* Chat Area */}
        <main className="flex-1 overflow-y-auto p-6 space-y-5">
          {messages.map((msg, index) => {
            const isUser = msg.sender === "user";
            return (
              <div
                key={index}
                className={`flex items-end gap-3 ${isUser ? "flex-row-reverse" : "flex-row"}`}
              >
                {/* Avatar */}
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
                    isUser ? "bg-blue-600 text-white" : "bg-slate-800 text-slate-300 border border-slate-700"
                  }`}
                >
                  {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                </div>

                {/* Message Bubble */}
                <div className={`max-w-[78%] flex flex-col ${isUser ? "items-end" : "items-start"}`}>
                  <div
                    className={`px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-line ${
                      isUser
                        ? "bg-blue-600 text-white rounded-br-none shadow-md shadow-blue-600/20"
                        : "bg-slate-800 text-slate-200 border border-slate-700/60 rounded-bl-none shadow-sm"
                    }`}
                  >
                    {msg.text}
                  </div>
                  <span className="text-[10px] text-slate-500 mt-1 px-1">{msg.time}</span>
                </div>
              </div>
            );
          })}

          {/* Loading Indicator */}
          {loading && (
            <div className="flex items-end gap-3">
              <div className="w-8 h-8 rounded-full bg-slate-800 text-slate-300 border border-slate-700 flex items-center justify-center shrink-0">
                <Bot className="w-4 h-4" />
              </div>
              <div className="bg-slate-800 border border-slate-700/60 text-slate-400 px-4 py-3 rounded-2xl rounded-bl-none flex items-center gap-2 text-sm">
                <Sparkles className="w-4 h-4 animate-spin text-blue-400" />
                <span>Agent is processing with tools...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </main>

        {/* Input Bar */}
        <footer className="p-4 bg-slate-900/80 border-t border-slate-800">
          <form onSubmit={handleSend} className="flex items-center gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about order status or cancellation (e.g. Check ORD101)..."
              disabled={loading}
              className="flex-1 bg-slate-950 border border-slate-800 text-slate-100 placeholder-slate-500 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="bg-blue-600 hover:bg-blue-500 active:scale-95 text-white font-medium p-3 rounded-xl transition-all disabled:opacity-40 disabled:hover:bg-blue-600 disabled:active:scale-100 flex items-center justify-center"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </footer>

      </div>
    </div>
  );
}