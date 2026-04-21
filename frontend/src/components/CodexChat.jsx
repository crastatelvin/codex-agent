import { useState } from "react";
import { askQuestion } from "../services/api";
import ReactMarkdown from "react-markdown";

export default function CodexChat({ hasRepo }) {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const send = async () => {
    if (!hasRepo || !input.trim() || loading) return;
    const question = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", text: question }]);
    setLoading(true);
    try {
      const res = await askQuestion(question);
      setMessages((prev) => [...prev, { role: "codex", text: res.answer }]);
    } catch {
      setMessages((prev) => [...prev, { role: "codex", text: "Failed to answer right now." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <div className="panel-title">CODEX Chat</div>
      <div className="chat-stream">
        {messages.length === 0 && <div className="muted">Ask about architecture, flows, modules, or where to implement features.</div>}
        {messages.map((m, i) => (
          <div key={i} className={`chat-item ${m.role}`}>
            <b style={{ textTransform: "uppercase", fontSize: ".72rem", color: "#7fffc2" }}>{m.role}</b>
            <div style={{ marginTop: ".3rem" }}>{m.role === "codex" ? <ReactMarkdown>{m.text}</ReactMarkdown> : m.text}</div>
          </div>
        ))}
      </div>
      <div style={{ display: "flex", gap: ".5rem", marginTop: ".75rem" }}>
        <input className="input" value={input} onChange={(e) => setInput(e.target.value)} placeholder="Ask a question about this codebase..." />
        <button className="btn btn-primary" onClick={send} disabled={!hasRepo || loading}>
          {loading ? "Thinking..." : "Ask"}
        </button>
      </div>
      {!hasRepo && <div className="muted" style={{ marginTop: ".55rem", fontSize: ".75rem" }}>Analyze a repository first to enable chat.</div>}
    </div>
  );
}
