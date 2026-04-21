export default function RepoStats({ data }) {
  const stats = [
    ["Files", data?.file_count || 0],
    ["Lines", data?.total_lines || 0],
    ["Functions", data?.total_functions || 0],
    ["Classes", data?.total_classes || 0],
  ];
  return (
    <div className="stats-grid">
      {stats.map(([label, value]) => (
        <div className="card" key={label}>
          <div style={{ fontSize: "1.32rem", color: "#00ff88", fontWeight: 700 }}>{value}</div>
          <div className="muted" style={{ fontSize: ".8rem" }}>
            {label}
          </div>
        </div>
      ))}
    </div>
  );
}
