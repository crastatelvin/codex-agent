import os
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from typing import Any

from dotenv import load_dotenv
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

_groq_client = None
_executor = ThreadPoolExecutor(max_workers=4)


def has_llm_configured() -> bool:
    return bool(os.getenv("GROQ_API_KEY", "").strip())


def _client() -> Groq:
    global _groq_client
    if _groq_client is None:
        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key:
            raise ValueError("GROQ_API_KEY is not set")
        _groq_client = Groq(api_key=api_key)
    return _groq_client


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=6))
def _generate(prompt: str) -> str:
    res = _client().chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.2,
        messages=[
            {"role": "system", "content": "You are CODEX, a senior software engineer and codebase onboarding assistant."},
            {"role": "user", "content": prompt},
        ],
    )
    return (res.choices[0].message.content or "").strip()


def _generate_with_timeout(prompt: str, timeout_s: int = 18) -> str:
    future = _executor.submit(_generate, prompt)
    try:
        return future.result(timeout=timeout_s)
    except FuturesTimeoutError:
        return ""
    except Exception:
        return ""


def explain_module(path: str, content: str, analysis: dict[str, Any]) -> str:
    prompt = f"""You are CODEX, expert code onboarding assistant.
Explain this file for a new engineer in 3-4 practical sentences.

FILE: {path}
LANGUAGE: {analysis.get("language", "unknown")}
FUNCTIONS: {[f["name"] for f in analysis.get("functions", [])[:15]]}
CLASSES: {[c["name"] for c in analysis.get("classes", [])[:10]]}

CODE:
{content[:1800]}
"""
    try:
        text = _generate_with_timeout(prompt)
        if text:
            return text
        return f"{path} contains core logic for {analysis.get('language', 'code')}."
    except Exception:
        return f"{path} contains core logic for {analysis.get('language', 'code')}."


def answer_codebase_question(question: str, context_chunks: list[dict[str, Any]], repo_info: dict[str, Any]) -> str:
    context = "\n\n---\n\n".join(
        f"File: {chunk['path']}\n{chunk['text'][:900]}" for chunk in context_chunks[:4]
    )
    prompt = f"""You are CODEX, a senior engineer onboarding someone into this repository.
Repository: {repo_info.get("full_name", "Unknown")}
Description: {repo_info.get("description", "")}

Code context:
{context}

Question: {question}

Answer in under 250 words. Be specific, cite file paths from context, and suggest next steps when useful.
"""
    try:
        text = _generate_with_timeout(prompt)
        if text:
            return text
        return "Unable to answer right now. Please retry."
    except Exception:
        return "Unable to answer right now. Please retry."


def generate_repo_summary(repo_info: dict[str, Any], analyses: list[dict[str, Any]], file_count: int) -> str:
    total_lines = sum(a.get("line_count", 0) for a in analyses)
    total_functions = sum(len(a.get("functions", [])) for a in analyses)
    prompt = f"""Summarize this repository in 4 sentences for developers.
Repo: {repo_info.get("full_name")}
Description: {repo_info.get("description", "")}
Primary language: {repo_info.get("language", "Unknown")}
Files analyzed: {file_count}
Total lines: {total_lines}
Functions detected: {total_functions}
"""
    try:
        text = _generate_with_timeout(prompt)
        if text:
            return text
        return f"{repo_info.get('full_name', 'Repository')} with {file_count} files analyzed."
    except Exception:
        return f"{repo_info.get('full_name', 'Repository')} with {file_count} files analyzed."
