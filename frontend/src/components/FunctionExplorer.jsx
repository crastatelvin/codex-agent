export default function FunctionExplorer({ analyses }) {
  const rows = (analyses || []).flatMap((a) =>
    (a.functions || []).map((fn) => ({
      path: a.path,
      name: fn.name,
      line: fn.line,
      isAsync: fn.is_async,
    }))
  );
  return (
    <div className="card">
      <div className="panel-title">Function Explorer</div>
      <div className="muted" style={{ marginBottom: ".6rem", fontSize: ".8rem" }}>
        Showing {Math.min(rows.length, 300)} / {rows.length} discovered functions
      </div>
      <div style={{ maxHeight: 560, overflow: "auto" }}>
        {rows.slice(0, 300).map((row) => (
          <div key={`${row.path}:${row.name}:${row.line}`} style={{ padding: ".34rem .2rem", borderBottom: "1px solid var(--border)" }}>
            <span className="pill" style={{ marginRight: ".5rem" }}>
              {row.path}
            </span>
          {row.isAsync ? "async " : ""}
            <strong>{row.name}</strong> <span className="muted">line {row.line}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
