import asyncio
import base64
import os
import re
from typing import Any

import httpx

MAX_FILES = int(os.getenv("MAX_FILES", "200"))
MAX_FILE_SIZE_KB = int(os.getenv("MAX_FILE_SIZE_KB", "100"))

SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".java",
    ".go",
    ".rs",
    ".cpp",
    ".c",
    ".cs",
    ".rb",
    ".php",
    ".swift",
    ".kt",
    ".scala",
    ".r",
    ".sql",
    ".sh",
    ".yaml",
    ".yml",
    ".json",
    ".toml",
    ".md",
    ".txt",
}


def parse_github_url(url: str) -> tuple[str, str]:
    clean = url.strip().rstrip("/")
    patterns = [
        r"github\.com[/:]([\w.-]+)/([\w.-]+?)(?:\.git)?$",
        r"^([\w.-]+)/([\w.-]+)$",
    ]
    for pattern in patterns:
        match = re.search(pattern, clean)
        if match:
            return match.group(1), match.group(2)
    raise ValueError(f"Invalid GitHub URL: {url}")


def _headers() -> dict[str, str]:
    github_token = os.getenv("GITHUB_TOKEN", "").strip()
    return {"Authorization": f"Bearer {github_token}"} if github_token else {}


def _raise_for_github_error(resp: httpx.Response, owner: str, repo: str) -> None:
    if resp.status_code == 404:
        raise ValueError(f"Repository {owner}/{repo} not found or is private")
    if resp.status_code == 403:
        reset_at = resp.headers.get("X-RateLimit-Reset")
        hint = "Add GITHUB_TOKEN to backend/.env and restart backend."
        if reset_at:
            raise ValueError(
                f"GitHub API rate limit exceeded for {owner}/{repo}. "
                f"Rate limit reset epoch: {reset_at}. {hint}"
            )
        raise ValueError(f"GitHub API rate limit exceeded for {owner}/{repo}. {hint}")
    resp.raise_for_status()


async def fetch_repo_info(owner: str, repo: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}",
            headers=_headers(),
        )
        _raise_for_github_error(resp, owner, repo)
        data = resp.json()
    return {
        "name": data["name"],
        "full_name": data["full_name"],
        "description": data.get("description", ""),
        "language": data.get("language", "Unknown"),
        "stars": data.get("stargazers_count", 0),
        "forks": data.get("forks_count", 0),
        "size_kb": data.get("size", 0),
        "default_branch": data.get("default_branch", "main"),
        "topics": data.get("topics", []),
        "url": data["html_url"],
    }


async def fetch_repo_tree(owner: str, repo: str, branch: str) -> list[dict[str, Any]]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1",
            headers=_headers(),
        )
        _raise_for_github_error(resp, owner, repo)
        tree = resp.json().get("tree", [])
    files: list[dict[str, Any]] = []
    for item in tree:
        if item.get("type") != "blob":
            continue
        path = item["path"]
        ext = "." + path.rsplit(".", 1)[-1] if "." in path else ""
        if ext.lower() not in SUPPORTED_EXTENSIONS:
            continue
        size_kb = item.get("size", 0) / 1024
        if size_kb <= MAX_FILE_SIZE_KB:
            files.append({"path": path, "size_kb": round(size_kb, 2)})
    return files[:MAX_FILES]


async def fetch_file_content(owner: str, repo: str, path: str, client: httpx.AsyncClient) -> str:
    resp = await client.get(
        f"https://api.github.com/repos/{owner}/{repo}/contents/{path}",
        headers=_headers(),
    )
    if resp.status_code != 200:
        return ""
    data = resp.json()
    if data.get("encoding") == "base64":
        try:
            return base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
        except Exception:
            return ""
    return data.get("content", "")


async def fetch_full_repo(owner: str, repo: str, branch: str, broadcast_fn) -> dict[str, Any]:
    await broadcast_fn({"step": "fetching", "message": "Fetching repository structure..."})
    files_list = await fetch_repo_tree(owner, repo, branch)
    await broadcast_fn({"step": "reading", "message": f"Reading {len(files_list)} files..."})

    sem = asyncio.Semaphore(12)
    files: dict[str, Any] = {}
    done = 0

    async with httpx.AsyncClient(timeout=20.0) as client:
        async def worker(file_meta: dict[str, Any]) -> None:
            nonlocal done
            async with sem:
                content = await fetch_file_content(owner, repo, file_meta["path"], client)
            if content:
                files[file_meta["path"]] = {
                    "path": file_meta["path"],
                    "content": content,
                    "size_kb": file_meta["size_kb"],
                    "lines": len(content.splitlines()),
                }
            done += 1
            if done % 10 == 0 or done == len(files_list):
                await broadcast_fn({"step": "reading", "message": f"Read {done}/{len(files_list)} files..."})

        await asyncio.gather(*(worker(item) for item in files_list))
    return files
