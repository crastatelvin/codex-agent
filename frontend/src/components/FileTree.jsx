function Node({ name, node, depth }) {
  const isDir = typeof node === "object" && node !== null;
  const indent = depth * 14;
  if (!isDir) {
    return (
      <div style={{ paddingLeft: indent, color: "var(--text-dim)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: ".35rem", padding: ".18rem 0" }}>
          <span style={{ width: 10, borderTop: "1px solid var(--border)" }} />
          <span>{name}</span>
        </div>
      </div>
    );
  }
  return (
    <div style={{ paddingLeft: indent }}>
      <div style={{ display: "flex", alignItems: "center", gap: ".35rem", padding: ".18rem 0" }}>
        {depth > 0 && <span style={{ width: 10, borderTop: "1px solid var(--border)" }} />}
        <strong style={{ color: "#7fffc2" }}>{name}</strong>
      </div>
      <div style={{ marginLeft: depth > 0 ? 10 : 0, borderLeft: "1px solid var(--border)", paddingLeft: ".35rem" }}>
        {Object.entries(node).map(([child, childNode]) => (
          <Node key={`${name}/${child}`} name={child} node={childNode} depth={depth + 1} />
        ))}
      </div>
    </div>
  );
}

export default function FileTree({ structure }) {
  return (
    <div className="card" style={{ maxHeight: 620, overflow: "auto" }}>
      <div className="panel-title">Repository Tree</div>
      {Object.entries(structure || {}).map(([name, node]) => (
        <Node key={name} name={name} node={node} depth={0} />
      ))}
    </div>
  );
}
