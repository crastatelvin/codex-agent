import UrlInput from "../components/UrlInput";

export default function LandingPage({ onAnalyze, loading }) {
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
    </div>
  );
}
