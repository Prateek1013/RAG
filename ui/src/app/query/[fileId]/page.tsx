"use client";
import React, { useState, useEffect, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { Navbar } from "@/components/Navbar";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { docClient } from "@/lib/api";
import { jwtDecode } from "jwt-decode";
import { Send, ArrowLeft, Bot, User } from "lucide-react";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
}

export default function QueryPage() {
  const params = useParams();
  const router = useRouter();
  const fileId = params.fileId as string;
  
  const [messages, setMessages] = useState<Message[]>([
    { id: "0", role: "assistant", content: "Hello! I am ready to answer questions about this document. What would you like to know?" }
  ]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [userId, setUserId] = useState<string>("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
      return;
    }
    try {
      const decoded: any = jwtDecode(token);
      setUserId(decoded.user_id);
    } catch (e) {
      router.push("/login");
    }
  }, [router]);

  // Fetch chat history
  useEffect(() => {
    if (!userId || !fileId) return;
    
    const fetchHistory = async () => {
      try {
        const res = await docClient.get(`/chat-history/${fileId}`);
        if (res.data.messages && res.data.messages.length > 0) {
          const loadedMessages = res.data.messages.map((m: any) => ({
            id: m.id,
            role: m.role,
            content: m.content
          }));
          // Add default welcome message if there are loaded messages
          setMessages([
            { id: "0", role: "assistant", content: "Welcome back! Here is your chat history for this document." },
            ...loadedMessages
          ]);
        }
      } catch (err) {
        console.error("Failed to load chat history", err);
      }
    };
    
    fetchHistory();
  }, [userId, fileId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || !userId) return;

    const userMessage: Message = { id: Date.now().toString(), role: "user", content: query };
    setMessages(prev => [...prev, userMessage]);
    setQuery("");
    setLoading(true);

    try {
      const res = await docClient.post("/query", {
        file_id: fileId,
        user_id: userId,
        query: userMessage.content
      });
      
      const assistantMessage: Message = { 
        id: (Date.now() + 1).toString(), 
        role: "assistant", 
        content: res.data.answer 
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      console.error("Query failed", err);
      const errorMessage: Message = { 
        id: (Date.now() + 1).toString(), 
        role: "assistant", 
        content: "Sorry, I encountered an error while trying to answer that." 
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen overflow-hidden">
      <Navbar />
      
      <main className="flex-1 flex flex-col max-w-4xl mx-auto w-full p-4 h-full relative min-h-0">
        <Card className="flex-1 flex flex-col min-h-0 relative mb-4">
          {/* Header area for back button */}
          <div className="p-3 border-b border-slate-700/50 bg-slate-900/50 rounded-t-xl shrink-0 flex items-center">
            <Button variant="ghost" size="sm" onClick={() => router.push("/dashboard")} className="gap-2 text-slate-400 hover:text-white">
              <ArrowLeft size={16} /> Back to Dashboard
            </Button>
          </div>

          {/* Chat History */}
          <div className="flex-1 overflow-y-auto p-4 space-y-6">
            {messages.map((msg) => (
              <div key={msg.id} className={`flex gap-4 ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                {msg.role === "assistant" && (
                  <div className="w-8 h-8 rounded-full bg-indigo-500/20 flex items-center justify-center shrink-0">
                    <Bot size={18} className="text-indigo-400" />
                  </div>
                )}
                
                <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                  msg.role === "user" 
                    ? "bg-indigo-600 text-white rounded-br-sm" 
                    : "bg-slate-800 text-slate-100 rounded-bl-sm border border-slate-700"
                }`}>
                  <p className="whitespace-pre-wrap text-sm leading-relaxed">{msg.content}</p>
                </div>

                {msg.role === "user" && (
                  <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center shrink-0">
                    <User size={18} className="text-slate-300" />
                  </div>
                )}
              </div>
            ))}
            {loading && (
              <div className="flex gap-4 justify-start">
                <div className="w-8 h-8 rounded-full bg-indigo-500/20 flex items-center justify-center shrink-0">
                  <Bot size={18} className="text-indigo-400" />
                </div>
                <div className="bg-slate-800 text-slate-400 rounded-2xl rounded-bl-sm px-4 py-3 border border-slate-700 flex items-center gap-1">
                  <span className="animate-bounce">.</span>
                  <span className="animate-bounce" style={{ animationDelay: "0.2s" }}>.</span>
                  <span className="animate-bounce" style={{ animationDelay: "0.4s" }}>.</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="p-4 border-t border-slate-700/50 bg-slate-900/50 rounded-b-xl">
            <form onSubmit={handleSend} className="flex gap-2">
              <Input 
                value={query} 
                onChange={(e) => setQuery(e.target.value)} 
                placeholder="Ask a question about this document..." 
                className="flex-1 rounded-full px-4"
                disabled={loading}
              />
              <Button type="submit" size="icon" className="rounded-full shrink-0" disabled={!query.trim() || loading}>
                <Send size={16} />
              </Button>
            </form>
          </div>
        </Card>
      </main>
    </div>
  );
}
