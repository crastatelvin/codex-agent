import { useState } from "react";
import ErrorBoundary from "./components/ErrorBoundary";
import MatrixBackground from "./components/MatrixBackground";
import ProcessingMatrix from "./components/ProcessingMatrix";
import useWebSocket from "./hooks/useWebSocket";
import LandingPage from "./pages/LandingPage";
import ExplorerPage from "./pages/ExplorerPage";
import { analyzeRepo } from "./services/api";
import "./styles/globals.css";

const nextAnalysisId = () => (globalThis.crypto?.randomUUID ? globalThis.crypto.randomUUID() : `${Date.now()}`);

export default function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [analysisId, setAnalysisId] = useState("");
  const [error, setError] = useState("");
  const currentStep = useWebSocket(analysisId);

  const onAnalyze = async (url) => {
    const runId = nextAnalysisId();
    setAnalysisId(runId);
    setLoading(true);
    setError("");
    try {
      const res = await analyzeRepo(url, runId);
      setAnalysisId(res.analysis_id || "");
      setData(res);
    } catch (e) {
      setError(e?.response?.data?.error || "Analysis failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <ErrorBoundary>
      <MatrixBackground />
      <ProcessingMatrix visible={loading} currentStep={currentStep} />
      {data ? <ExplorerPage data={data} onReset={() => setData(null)} /> : <LandingPage onAnalyze={onAnalyze} loading={loading} />}
      {error && <div className="error-toast">{error}</div>}
    </ErrorBoundary>
  );
}
