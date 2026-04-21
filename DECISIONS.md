# Architecture Decisions

- Use GitHub REST API instead of `git clone` to avoid filesystem-heavy operations on free-tier hosting.
- Use Python AST for Python files and regex heuristics for JS/TS for lightweight multi-language analysis.
- Use Groq for explanations/Q&A and local FastEmbed for embeddings, since Groq does not provide embeddings.
- Use ChromaDB persistent client to keep vector index available across backend restarts.
- Use per-analysis WebSocket channels to avoid broadcasting progress to unrelated sessions.
