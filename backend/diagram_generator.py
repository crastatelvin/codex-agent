from typing import Any


def _module_name(path: str) -> str:
    return path.replace("/", "_").replace(".", "_").replace("-", "_")


def generate_mermaid_diagram(analyses: list[dict[str, Any]], repo_name: str) -> str:
    lines = ["graph TD"]
    nodes = set()
    edges = set()
    by_basename = {}
    for analysis in analyses[:60]:
        path = analysis["path"]
        node = _module_name(path)
        label = path.split("/")[-1][:30].replace('"', "'")
        nodes.add((node, label))
        by_basename[path.split("/")[-1].rsplit(".", 1)[0].lower()] = node
    for analysis in analyses[:60]:
        src = _module_name(analysis["path"])
        for imp in analysis.get("imports", []):
            target = by_basename.get(imp.lower())
            if target and target != src:
                edges.add((src, target))
    for node, label in list(nodes)[:35]:
        lines.append(f'    {node}["{label}"]')
    edge_list = list(edges)
    if not edge_list:
        node_ids = [node for node, _label in list(nodes)[:18]]
        for i in range(len(node_ids) - 1):
            edge_list.append((node_ids[i], node_ids[i + 1]))
    for src, dst in edge_list[:80]:
        lines.append(f"    {src} --> {dst}")
    return "\n".join(lines)


def generate_class_diagram(analyses: list[dict[str, Any]]) -> str:
    lines = ["classDiagram"]
    class_names = []
    for analysis in analyses[:30]:
        for cls in analysis.get("classes", [])[:4]:
            cls_name = cls["name"].replace("-", "_")
            class_names.append(cls_name)
            lines.append(f"    class {cls_name} {{")
            for method in cls.get("methods", [])[:10]:
                lines.append(f"        +{method}()")
            lines.append("    }")
    if len(class_names) > 1:
        for i in range(len(class_names) - 1):
            lines.append(f"    {class_names[i]} --> {class_names[i + 1]}")
    return "\n".join(lines) if len(lines) > 1 else "classDiagram\n    class NoClasses"
