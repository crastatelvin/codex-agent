import UrlInput from "../components/UrlInput";

export default function LandingPage({ onAnalyze, loading, history = [] }) {
  return (
    <div className="hero-shell">
      <h1 className="headline">CODEX</h1>
      <p className="subhead">Paste any GitHub URL to analyze architecture, understand modules, and ask targeted questions.</p>
      <div className="pill-row">
        <span className="pill">Architecture map</span>
        <span className="pill">Function explorer</span>
        <span className="pill">AI guided Q&A</span>
        <span className="pill">Repo onboarding</span>
      </div>
      <UrlInput onAnalyze={onAnalyze} loading={loading} />
      
      {history.length > 0 && (
        <div style={{ marginTop: "2rem", width: "100%", maxWidth: 500 }}>
          <div className="muted" style={{ fontSize: ".8rem", marginBottom: ".75rem", textAlign: "center", textTransform: "uppercase", letterSpacing: "1px" }}>
            Recent Repositories
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: ".5rem" }}>
            {history.map((url) => (
              <button
                key={url}
                onClick={() => onAnalyze(url)}
                className="btn"
                style={{ textAlign: "left", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", display: "block", width: "100%", padding: ".6rem 1rem" }}
              >
                {url.replace("https://github.com/", "")}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
