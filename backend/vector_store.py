from typing import Any

indexed_chunks: list[dict[str, Any]] = []


def init_collection(repo_name: str) -> None:
    global indexed_chunks
    indexed_chunks = []


def index_file(path: str, content: str, analysis: dict[str, Any]) -> None:
    chunk = f"File: {path}\n\n{content[:3500]}"
    indexed_chunks.append(
        {
            "text": chunk,
            "path": path,
            "language": analysis.get("language", ""),
        }
    )


def search_code(query_text: str, n: int = 5) -> list[dict[str, Any]]:
    if not indexed_chunks:
        return []
    terms = [t.lower() for t in query_text.split() if t.strip()]
    if not terms:
        return [{"text": c["text"], "path": c["path"], "distance": 0.0} for c in indexed_chunks[:n]]
    scored = []
    for chunk in indexed_chunks:
        hay = chunk["text"].lower()
        score = sum(hay.count(term) for term in terms)
        if score > 0:
            scored.append((score, chunk))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [
        {"text": c["text"], "path": c["path"], "distance": float(1 / (s + 1))}
        for s, c in scored[:n]
    ]
