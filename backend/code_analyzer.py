import ast
import re
from typing import Any


def analyze_python_file(content: str, path: str) -> dict[str, Any]:
    functions = []
    classes = []
    imports = []
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                doc = ast.get_docstring(node) or ""
                functions.append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                        "args": [a.arg for a in node.args.args],
                        "docstring": doc[:200],
                        "is_async": isinstance(node, ast.AsyncFunctionDef),
                    }
                )
            elif isinstance(node, ast.ClassDef):
                classes.append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                        "methods": [
                            n.name
                            for n in ast.walk(node)
                            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                        ][:20],
                    }
                )
            elif isinstance(node, ast.Import):
                imports.extend(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.append(node.module.split(".")[0])
    except SyntaxError:
        pass
    return {
        "path": path,
        "language": "python",
        "functions": functions[:50],
        "classes": classes[:20],
        "imports": list(set(imports))[:40],
        "line_count": len(content.splitlines()),
    }


def analyze_js_ts_file(content: str, path: str) -> dict[str, Any]:
    functions = []
    imports = []
    func_patterns = [
        r"(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+(\w+)",
        r"(?:export\s+)?const\s+(\w+)\s*=\s*(?:async\s+)?\(",
    ]
    for pattern in func_patterns:
        for match in re.finditer(pattern, content):
            name = match.group(1)
            if name:
                functions.append({"name": name, "line": content[: match.start()].count("\n") + 1})
    import_pattern = r"(?:import|require)\s*(?:\{[^}]*\}|[\w*]+)\s*(?:from\s*)?[\"']([^\"']+)[\"']"
    for match in re.finditer(import_pattern, content):
        imports.append(match.group(1).split("/")[0].replace("@", ""))
    return {
        "path": path,
        "language": "javascript" if path.endswith((".js", ".jsx")) else "typescript",
        "functions": list({f["name"]: f for f in functions}.values())[:50],
        "classes": [],
        "imports": list(set(imports))[:40],
        "line_count": len(content.splitlines()),
    }


def analyze_file(content: str, path: str) -> dict[str, Any]:
    if path.endswith(".py"):
        return analyze_python_file(content, path)
    if path.endswith((".js", ".jsx", ".ts", ".tsx")):
        return analyze_js_ts_file(content, path)
    return {
        "path": path,
        "language": path.rsplit(".", 1)[-1] if "." in path else "text",
        "functions": [],
        "classes": [],
        "imports": [],
        "line_count": len(content.splitlines()),
    }


def build_repo_structure(files: dict[str, Any]) -> dict[str, Any]:
    structure: dict[str, Any] = {}
    for path in files:
        parts = path.split("/")
        cursor = structure
        for part in parts[:-1]:
            cursor = cursor.setdefault(part, {})
        cursor[parts[-1]] = "file"
    return structure


def get_language_breakdown(analyses: list[dict[str, Any]]) -> dict[str, int]:
    out: dict[str, int] = {}
    for analysis in analyses:
        lang = analysis.get("language", "other")
        out[lang] = out.get(lang, 0) + analysis.get("line_count", 0)
    return out
