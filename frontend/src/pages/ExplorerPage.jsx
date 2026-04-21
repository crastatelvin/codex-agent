import { useState } from "react";
import ArchitectureDiagram from "../components/ArchitectureDiagram";
import CodexChat from "../components/CodexChat";
import FileTree from "../components/FileTree";
import FunctionExplorer from "../components/FunctionExplorer";
import ModuleCard from "../components/ModuleCard";
import RepoStats from "../components/RepoStats";

export default function ExplorerPage({ data, onReset }) {
  const [tab, setTab] = useState("modules");
  const tabs = ["modules", "architecture", "functions", "chat"];

  return (
    <div className="page-shell">
      <div className="card" style={{ marginBottom: "1rem" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: ".8rem", flexWrap: "wrap" }}>
          <div>
            <div className="muted" style={{ fontSize: ".72rem", textTransform: "uppercase", letterSpacing: ".08em" }}>
              Repository
            </div>
            <h2 style={{ margin: ".18rem 0 0", fontSize: "1.24rem", color: "#98ffd0" }}>{data?.repo_info?.full_name}</h2>
            <p className="muted" style={{ margin: ".35rem 0 0", fontSize: ".78rem" }}>
              {data?.summary || "Analysis complete"}
            </p>
          </div>
          <button className="btn" onClick={onReset}>
            Analyze New Repository
          </button>
        </div>
      </div>
      <RepoStats data={data} />
      <div className="tabs">
        {tabs.map((name) => (
          <button key={name} className={`btn tab-btn ${tab === name ? "active" : ""}`} onClick={() => setTab(name)}>
            {name[0].toUpperCase() + name.slice(1)}
          </button>
        ))}
      </div>
      <div className="explorer-grid">
        <FileTree structure={data?.structure} />
        <div>
          {tab === "modules" &&
            <div className="module-list">
              {data?.analyses?.map((analysis) => (
                <ModuleCard key={analysis.path} analysis={analysis} explanation={data?.module_explanations?.[analysis.path]} />
              ))}
            </div>}
          {tab === "architecture" && (
            <div className="module-list">
              <ArchitectureDiagram title="Module Dependencies" diagram={data?.mermaid_diagram} />
              <ArchitectureDiagram title="Class Diagram" diagram={data?.class_diagram} />
            </div>
          )}
          {tab === "functions" && <FunctionExplorer analyses={data?.analyses || []} />}
          {tab === "chat" && <CodexChat hasRepo={!!data} />}
        </div>
      </div>
    </div>
  );
}
