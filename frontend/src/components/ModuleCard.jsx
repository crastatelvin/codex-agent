export default function ModuleCard({ analysis, explanation }) {
  return (
    <div className="card">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: ".7rem" }}>
        <div style={{ fontWeight: 700, fontSize: ".94rem" }}>{analysis.path}</div>
        <div className="pill">{analysis.language}</div>
      </div>
      <div className="muted" style={{ marginTop: ".35rem", fontSize: ".78rem" }}>
        {analysis.line_count} lines • {analysis.functions?.length || 0} functions • {analysis.classes?.length || 0} classes
      </div>
      <div style={{ marginTop: ".65rem", fontSize: ".89rem" }}>{explanation || "No explanation available."}</div>
    </div>
  );
}
