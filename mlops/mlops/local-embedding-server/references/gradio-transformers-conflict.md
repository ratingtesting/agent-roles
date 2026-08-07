# gradio 6 vs transformers 4.x — huggingface-hub conflict

## Symptom
After installing deps in the order: numpy/torch/transformers/sentence-transformers → onnxruntime/fastapi → utils → huggingface-hub>=0.30.0 + optimum[onnxruntime] → h2/gradio/pytest, the server fails at import:

```
ImportError: huggingface-hub>=0.34.0,<1.0 is required for a normal functioning of this module, but found huggingface-hub==1.23.0.
```

## Root cause
`gradio 6.20.0` requires `huggingface-hub<2.0,>=1.2.0`. Because it is installed LAST, pip lets it upgrade
`huggingface-hub` to 1.23.0, which is incompatible with `transformers 4.57.6` (needs `<1.0`).

## Fix (verified working)
```bash
.venv/Scripts/pip install "huggingface-hub==0.36.2"   # transformers accepts this
.venv/Scripts/pip install "gradio==4.44.1"            # 4.x needs only huggingface-hub>=0.19.3, compatible with 0.36.2
```
After this: `python -c "from lightweight_embeddings.main import create_app"` imports OK.

## Notes
- transformers + optimum must stay on the 4.x / 2.x line; do NOT let gradio pull hf-hub >=1.0.
- If you must use gradio 6, you'd need transformers 5.x (not present in this repo's constraints) — avoid.
- `pip`'s dependency resolver does not auto-downgrade conflicts; you must pin explicitly and install the pin LAST.
