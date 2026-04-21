import { useState } from "react";

export default function UrlInput({ onAnalyze, loading }) {
  const [url, setUrl] = useState("");
  return (
    <div className="card" style={{ display: "flex", gap: ".6rem", alignItems: "center" }}>
      <input className="input" value={url} onChange={(e) => setUrl(e.target.value)} placeholder="https://github.com/owner/repo" />
      <button className="btn btn-primary" disabled={loading || !url.trim()} onClick={() => onAnalyze(url)}>
        {loading ? "Analyzing..." : "Analyze"}
      </button>
    </div>
  );
}
