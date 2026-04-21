export default function ProcessingMatrix({ visible, currentStep }) {
  if (!visible) return null;
  return (
    <div style={{ position: "fixed", inset: 0, display: "grid", placeItems: "center", background: "rgba(0,0,0,0.82)", zIndex: 99 }}>
      <div className="card" style={{ width: 420, textAlign: "center" }}>
        <div style={{ color: "#00ff88", fontWeight: 800, marginBottom: ".5rem", letterSpacing: ".08em" }}>CODEX ANALYZING</div>
        <div className="muted">{currentStep || "Analyzing repository..."}</div>
      </div>
    </div>
  );
}
