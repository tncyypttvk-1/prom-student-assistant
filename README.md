# Prom · Prometheus University

![Prom project cover](docs/linkedin-cover.png)

**Final Colab:** [Executed notebook](https://colab.research.google.com/drive/1-NL5VZoQhPoZOFM7Hq5MaNHQ85zae99j?usp=sharing)

**Explore:** [University showcase](https://tncyypttvk-1.github.io/prom-student-assistant/) · [LinkedIn draft](docs/LINKEDIN.md)

A bilingual Turkish/English student affairs assistant built as an AI Engineering capstone. Prometheus University is a **fictional educational institution**. This project does not perform official student transactions.

## What this repository contains

- `notebooks/Prom_Bitirme_Projesi.ipynb`: Colab pipeline for synthetic data, QLoRA fine-tuning, evaluation, RAG, agents, GGUF and Gradio deployment.
- `src/`: identity, shared agent tools, weighted GPA calculator and retrieval patch.
- `data/`: 15 bilingual guide sections, 11 course records, 30 test questions.
- `site/dist/`: responsive, buildless university showcase, guide explorer, course catalog and browser-local GPA calculator. The Prom button opens the trained model through a **temporary Colab/Gradio demo**. The runtime must remain active.
- `docs/results.json`: results shared from Colab, with known limitations.
- `docs/`: architecture, reproducibility notes, GitHub publishing instructions and LinkedIn draft.

## Architecture

`Student question → fine-tuned Qwen → RAG / course lookup / calculator / weighted GPA → answer`

Base model: `Qwen/Qwen2.5-1.5B-Instruct`. Fine-tuning: QLoRA, rank 16, alpha 32, 3 epochs. Identity and tool protocol are shared across training and the Gradio application. Chroma with multilingual embeddings provides notebook retrieval; the original CPU Space pipeline uses TF-IDF. The cleaned-retrieval patch is separately included and its improvement has not yet been verified.

## Results and honest limits

Final executed notebook reviewed on 17 October 2026: **23.5 / 30 = 0.7833** (displayed as 0.78). TR **0.7333**, EN **0.8333**. These are Gemini-judge scores on a small test suite, including retrieval and application-level agent fixes. Rule-based GPA routing contributes and is not model-only performance. The 0.77 preceding run and older 0.52/0.70 runs are separate records; judge variation was observed.

| Metric | TR before / after | EN before / after |
|---|---|---|
| Name mention | 0.00 / 0.50 | 0.00 / 0.40 |
| Correct tool | 0.00 / 0.67 | 0.00 / 0.60 |
| RAG judge | 0.50 / 0.47 | 0.60 / 1.00 |

These before/after metrics precede application fixes. Turkish RAG did not improve in this measurement. Known failures include attendance, registration-freeze and overdue-book answers, institution/developer identity, language mismatch and incomplete answers. Only three CPU examples were checked; 0.78 is not a CPU benchmark.

The repository notebook is an earlier source snapshot; use the **Final Colab** link above for the latest executed notebook and historical training evidence. The latest run reused the trained model; it did not retrain.

## Run the showcase locally

```sh
python3 -m http.server 8000 --directory site/dist
```

Open `http://localhost:8000`. No package installation or model download is required for the showcase.

## Run training

Upload the notebook to Google Colab, select T4 GPU, store a write-capable Hugging Face token as `HF_TOKEN` in Colab Secrets, and upload `data/rehber.pdf`, `data/dersler.csv`, `data/test_sorulari.csv` and `data/rehber_bolumleri.json`. Run cells in order. Review generated data before training. The notebook targets 720 candidate examples and checks for at least 600 unique training examples; these targets are not a verified actual training count. Save notebook outputs and checkpoints before a Colab session ends.

Never commit access tokens, private student records or model weights. Uploaded weights, dataset and Space URLs must be recorded only once their availability has been verified.

## GitHub Pages

The included workflow deploys `site/dist` when enabled in repository Settings → Pages → GitHub Actions. This serves the static showcase; hosting the trained model requires the separate Gradio/GGUF runtime. The temporary model URL is configured in `site/dist/demo-config.js`. Replace it with a verified permanent `hf.space` app URL when available. No access token belongs in browser code.

## Credits and licensing

Adapted from the Tech İstanbul capstone sample supplied in the course. The university guide and sample data originate from its fictional university package. Base-model license is Apache-2.0; verify upstream sample/data redistribution terms before assigning a blanket repository license. No blanket license is asserted here.
