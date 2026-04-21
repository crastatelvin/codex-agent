from fastapi.testclient import TestClient

from code_analyzer import analyze_file, build_repo_structure, get_language_breakdown
from github_fetcher import parse_github_url
import main
from main import app


def test_parse_github_url_full():
    owner, repo = parse_github_url("https://github.com/tiangolo/fastapi")
    assert owner == "tiangolo"
    assert repo == "fastapi"


def test_parse_github_url_short():
    owner, repo = parse_github_url("owner/repo")
    assert owner == "owner"
    assert repo == "repo"


def test_python_analyzer_detects_async():
    content = """
import os

class A:
    async def run(self, x):
        return x

def sync_func(a, b):
    return a + b
"""
    analysis = analyze_file(content, "sample.py")
    names = {f["name"]: f for f in analysis["functions"]}
    assert "run" in names
    assert names["run"]["is_async"] is True
    assert "sync_func" in names
    assert names["sync_func"]["is_async"] is False


def test_structure_and_language_breakdown():
    files = {"src/main.py": {"content": "print(1)"}, "web/app.ts": {"content": "export const a = 1"}}
    structure = build_repo_structure(files)
    assert "src" in structure
    assert "web" in structure
    analyses = [analyze_file("print(1)\n", "src/main.py"), analyze_file("export const a=1\n", "web/app.ts")]
    langs = get_language_breakdown(analyses)
    assert langs["python"] >= 1
    assert langs["typescript"] >= 1


def test_health_and_status_endpoints():
    client = TestClient(app)
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["ok"] is True
    status = client.get("/status")
    assert status.status_code == 200
    assert "has_repo" in status.json()


def test_analyze_endpoint_with_mocked_dependencies(monkeypatch):
    async def fake_repo_info(owner, repo):
        return {
            "name": repo,
            "full_name": f"{owner}/{repo}",
            "description": "mock repo",
            "language": "Python",
            "stars": 1,
            "forks": 0,
            "size_kb": 10,
            "default_branch": "main",
            "topics": [],
            "url": f"https://github.com/{owner}/{repo}",
        }

    async def fake_full_repo(owner, repo, branch, broadcast_fn):
        await broadcast_fn({"step": "reading", "message": "mock read"})
        return {
            "src/app.py": {
                "path": "src/app.py",
                "content": "def hello(name):\n    return name\n",
                "size_kb": 1.2,
                "lines": 2,
            }
        }

    monkeypatch.setattr(main, "fetch_repo_info", fake_repo_info)
    monkeypatch.setattr(main, "fetch_full_repo", fake_full_repo)
    monkeypatch.setattr(main, "index_file", lambda *args, **kwargs: None)
    monkeypatch.setattr(main, "init_collection", lambda repo: None)
    monkeypatch.setattr(main, "generate_repo_summary", lambda *args, **kwargs: "Mock summary")

    client = TestClient(app)
    response = client.post("/analyze", json={"url": "https://github.com/example/repo", "analysis_id": "test-run"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["repo_info"]["full_name"] == "example/repo"
    assert payload["file_count"] == 1
    assert payload["analysis_id"] == "test-run"


def test_ask_endpoint_with_mocked_search_and_llm(monkeypatch):
    main.repo_store["current"] = {
        "repo_info": {"full_name": "example/repo", "description": "mock", "language": "Python"}
    }
    monkeypatch.setattr(
        main,
        "search_code",
        lambda question, n=5: [{"path": "src/app.py", "text": "def hello():\n    return 'ok'", "distance": 0.1}],
    )
    monkeypatch.setattr(main, "answer_codebase_question", lambda q, c, r: "Mock answer for ask endpoint")

    client = TestClient(app)
    response = client.post("/ask", json={"question": "What does this repo do?"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"] == "Mock answer for ask endpoint"
    assert payload["sources"] == ["src/app.py"]
