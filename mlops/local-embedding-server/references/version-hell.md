# Version Hell Transcript — torch 2.13 + optimum + sentence-transformers

## The conflict chain

```
torch 2.13  ─── removed from torch.onnx.symbolic_opset14:
                _attention_scale
                _causal_attention_mask
                _onnx_symbolic
                _type_utils
                jit_utils
                symbolic_helper
                  │
                  ▼
optimum 1.x ─── imports ALL of the above in
                optimum/exporters/onnx/model_patcher.py:346
                  → ImportError: cannot import name '...'
                  │
                  ▼
optimum 2.2+ ─── dropped ONNX_WEIGHTS_NAME from
                optimum.onnxruntime top-level
                  → sentence-transformers load_onnx_model fails
                  │
                  ▼
sentence-transformers 5.6 ─── removed DISABLE_ONNX env var
                all models forced through ONNX backend
```

## Working combo (discovered experimentally)

| Package           | Version  | Why                                                              |
|-------------------|----------|------------------------------------------------------------------|
| torch             | 2.13.0   | Only wheel on Windows CPU. _attention_scale removed.              |
| optimum           | 2.0.0    | Has ONNX_WEIGHTS_NAME + works with torch 2.13                    |
| optimum-onnx      | 0.0.3    | Installed as dep of optimum[onnxruntime]                          |
| transformers      | 4.55.4   | Pinned by optimum 2.0. Requires tokenizers<0.22                   |
| tokenizers        | 0.21.4   | transformers 4.55 constraint                                      |
| huggingface-hub   | 0.36.2   | Gradio would pull 1.23.0, breaking transformers                   |
| gradio            | 4.44.1   | Gradio≥6 forces hf-hub≥1.2                                       |
| sentence-transformers | 5.6.0 | No DISABLE_ONNX — ONNX mandatory                                 |
| onnxruntime       | 1.27.0   | Latest, compatible with optimum 2.0                               |

## Failed attempts

1. **optimum 1.27 patch model_patcher.py** → fixed _attention_scale,
   but _causal_attention_mask, _onnx_symbolic also removed;
   endless whack-a-mole.

2. **Remove optimum + use BAAI/bge-m3 PyTorch** → sentence-transformers
   5.6 forces ONNX loader even for non-ONNX models.

3. **optimum 2.2.0** → ONNX_WEIGHTS_NAME removed from public API.

4. **`unset PYTHONPATH` + standard python -m venv** → still get
   activation contamination from Hermes.

5. **`SENTENCE_TRANSFORMERS_DISABLE_ONNX=1`** → removed in 5.x,
   silently ignored.
