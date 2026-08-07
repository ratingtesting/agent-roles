# Rerank in lightweight-embeddings

REST endpoint: **`POST /v1/rank`** (NOT `/v1/rerank`).

```bash
curl http://localhost:7860/v1/rank \
  -H "Content-Type: application/json" \
  -d '{
    "model": "bge-m3",
    "queries": "happy person",
    "candidates": ["sad dog", "sunny day", "That is a very happy person"]
  }'
```

Fields: `queries` (str | list[str]), `candidates` (list[str]).

Response: `cosine_similarities` (list of lists) + `probabilities` (softmax-normalized) + `usage`.

Implementation in `api/routes/rank.py` calls `service.rank()` which:
1. Generates embeddings for all queries + candidates via `asyncio.gather` (parallel).
2. Computes **cosine similarity** between each query and each candidate.
3. Applies **softmax** to get probabilities.

The UI **Rerank** tab (`web/ui.py` line 112, `rank_handler`) calls the same `service.rank()`.

**Important:** This is cosine similarity on bge-m3 embeddings, **not** a cross-encoder. The model is the same bge-m3 ONNX model — no separate reranker.

For a proper cross-encoder reranker, use `cross-encoder/ms-marco-MiniLM-L-6-v2` or similar separately.
