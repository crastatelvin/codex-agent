import json
import logging
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl

from code_analyzer import analyze_file, build_repo_structure, get_language_breakdown
from diagram_generator import generate_class_diagram, generate_mermaid_diagram
from llm_service import answer_codebase_question, generate_repo_summary, has_llm_configured
from github_fetcher import fetch_full_repo, fetch_repo_info, parse_github_url
from vector_store import index_file, init_collection, search_code

app = FastAPI(title="CODEX - AI Codebase Onboarding Agent")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
logger = logging.getLogger("codex")

connections: dict[str, list[WebSocket]] = {}
repo_store: dict[str, Any] = {}
STORE_FILE = Path("./repo_store.json")


class AnalyzeRequest(BaseModel):
    url: HttpUrl
    analysis_id: str | None = None


class AskRequest(BaseModel):
    question: str


def _load_store() -> None:
    if STORE_FILE.exists():
        try:
            repo_store.update(json.loads(STORE_FILE.read_text(encoding="utf-8")))
        except Exception:
            return


def _save_store() -> None:
    try:
        STORE_FILE.write_text(json.dumps(repo_store), encoding="utf-8")
    except Exception:
        return


async def broadcast(analysis_id: str, data: dict[str, Any]) -> None:
    subs = connections.get(analysis_id, [])
    for ws in subs[:]:
        try:
            await ws.send_text(json.dumps(data))
        except Exception:
            subs.remove(ws)


@app.on_event("startup")
async def startup() -> None:
    _load_store()
    if not has_llm_configured():
        logger.warning("GROQ_API_KEY is not set. /analyze and /ask will return fallback responses.")


@app.websocket("/ws/{analysis_id}")
async def ws_endpoint(websocket: WebSocket, analysis_id: str) -> None:
    await websocket.accept()
    connections.setdefault(analysis_id, []).append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connections.get(analysis_id, []).remove(websocket)


@app.get("/")
def root() -> dict[str, Any]:
    return {"status": "CODEX ONLINE", "version": "1.0"}


@app.get("/health")
def health() -> dict[str, Any]:
    return {"ok": True}


@app.post("/analyze")
async def analyze_repo(body: AnalyzeRequest):
    analysis_id = body.analysis_id or str(uuid.uuid4())
    try:
        owner, repo = parse_github_url(str(body.url))
        await broadcast(analysis_id, {"step": "info", "message": f"Fetching {owner}/{repo}..."})
        repo_info = await fetch_repo_info(owner, repo)
        files = await fetch_full_repo(owner, repo, repo_info["default_branch"], lambda d: broadcast(analysis_id, d))
        await broadcast(analysis_id, {"step": "analyzing", "message": f"Analyzing {len(files)} files..."})

        analyses = []
        module_explanations = {}
        init_collection(repo)
        for index, (path, file_data) in enumerate(files.items()):
            analysis = analyze_file(file_data["content"], path)
            analyses.append(analysis)
            try:
                index_file(path, file_data["content"], analysis)
            except Exception:
                pass
            if analysis["functions"] or analysis["classes"]:
                module_explanations[path] = (
                    f"{analysis['language']} module with "
                    f"{len(analysis['functions'])} functions and {len(analysis['classes'])} classes."
                )
            await broadcast(analysis_id, {"step": "analyzing", "message": f"Analyzed {index + 1}/{len(files)} files..."})

        mermaid_diagram = generate_mermaid_diagram(analyses, repo)
        class_diagram = generate_class_diagram(analyses)
        summary = generate_repo_summary(repo_info, analyses, len(files))
        structure = build_repo_structure(files)
        lang_breakdown = get_language_breakdown(analyses)

        repo_store["current"] = {
            "repo_info": repo_info,
            "analyses": analyses[:100],
            "files": {p: {"lines": f["lines"], "size_kb": f["size_kb"]} for p, f in files.items()},
        }
        _save_store()
        result = {
            "analysis_id": analysis_id,
            "repo_info": repo_info,
            "summary": summary,
            "file_count": len(files),
            "total_lines": sum(a.get("line_count", 0) for a in analyses),
            "total_functions": sum(len(a.get("functions", [])) for a in analyses),
            "total_classes": sum(len(a.get("classes", [])) for a in analyses),
            "language_breakdown": lang_breakdown,
            "analyses": analyses[:100],
            "module_explanations": module_explanations,
            "mermaid_diagram": mermaid_diagram,
            "class_diagram": class_diagram,
            "structure": structure,
        }
        await broadcast(analysis_id, {"step": "complete", "message": "Codebase analysis complete!"})
        return JSONResponse(result)
    except Exception as exc:
        await broadcast(analysis_id, {"step": "error", "message": str(exc)})
        return JSONResponse(status_code=500, content={"error": str(exc), "analysis_id": analysis_id})


@app.post("/ask")
async def ask_question(body: AskRequest):
    question = body.question.strip()
    if not question:
        return JSONResponse(status_code=400, content={"error": "Question required"})
    if "current" not in repo_store:
        return JSONResponse(status_code=400, content={"error": "No repository analyzed yet"})
    repo_info = repo_store["current"]["repo_info"]
    try:
        chunks = search_code(question, n=5)
    except Exception:
        chunks = []
    answer = answer_codebase_question(question, chunks, repo_info)
    return JSONResponse({"question": question, "answer": answer, "sources": [c["path"] for c in chunks[:3]]})


@app.get("/status")
def status():
    has_repo = "current" in repo_store
    return JSONResponse({"has_repo": has_repo, "repo": repo_store.get("current", {}).get("repo_info", {}).get("full_name", "")})
