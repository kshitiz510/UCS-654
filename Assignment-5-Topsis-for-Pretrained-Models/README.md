# TOPSIS Evaluation of Pretrained Sentence-Transformers

This folder contains an experimental notebook that evaluates a set of pretrained Sentence Transformer models on the STS-B (Semantic Textual Similarity Benchmark) test split and ranks them using TOPSIS. This README explains the methodology, the expected result table, how to produce result graphs, and how to run the notebook.

## Purpose

Evaluate pretrained `sentence-transformers/*` on STS-B (GLUE) and rank models with TOPSIS
using three criteria: Accuracy (Spearman), Time (ms), and Size (MB).

## Quick run

1. Install minimal dependencies:

```bash
pip install -r requirements.txt
```

2. Open `notebook.ipynb` and run cells (first run downloads models to HF cache).

## Results

The notebook prints a clean DataFrame `df` with:

- `Model` — short name
- `Accuracy` — Spearman correlation
- `Time_ms` — avg inference time per pair (ms)
- `Size_MB` — estimated model size from HF cache (may be NaN)
- `TOPSIS_Score`, `Rank`

## Method (brief)

1. Encode sentence pairs with `SentenceTransformer` and compute cosine similarity.
2. Compute Spearman correlation against STS-B labels (used as `Accuracy`).
3. Estimate model size from local HF cache (if present).
4. Build decision matrix [Accuracy, Time_ms, Size_MB], normalize, apply weights,
   compute distances to ideal best/worst, then TOPSIS score $C_i = D_i^-/(D_i^+ + D_i^-)$.

Weights (default): `w = [0.50, 0.30, 0.20]` (Accuracy prioritized).

## Notes

- `Size_MB` may be `NaN` until a model is downloaded to the HF cache.
- Timing varies by hardware; for repeatability set `device='cpu'` or run on the same device.
- If Spearman is NaN, the notebook sets `Accuracy` to 0.0 for display.

## Files

- `notebook.ipynb` — evaluation and TOPSIS pipeline

If you want this shorter (one-liner) or exactly 80 lines, tell me and I will adjust.
If you'd like, I can also add a small script to run the notebook headlessly and save a CSV with results and the generated PNGs. Would you like that?
