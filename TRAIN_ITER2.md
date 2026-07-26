# chaosnexus-tuned/TRAIN_ITER2.md

# Train iteration-2 plan (post eval hold)

**Trigger:** Iteration-1 mean **0.444** (&lt;0.70) and smoke Fail on prompts 4 and 5.  
**Gates (dual):** alpha publish ≥0.70; full-version claim ≥0.90; hold if &lt;0.70.

## Dataset (built)

- Injector: `scripts/injectors/inject_iter2_api_goldens.py`
- Output: `datasets/iter2/train.jsonl` (+ `datasets/iter2/build_meta.json`)
- Source base filtered from: `datasets/augmented/train_augmented.jsonl` (poisoned invented-API rows dropped)
- Studio YAML: `unsloth_training/ChaosNexus_Tuned.yaml` → `dataset_path: datasets/iter2/train.jsonl`

## Train

```bash
cd chaosnexus-tuned
# AMD ROCm (Unsloth package rejects non-NVIDIA):
HIP_VISIBLE_DEVICES=0 ~/.unsloth/studio/unsloth_studio/bin/python train_peft_rocm.py \
  --dataset datasets/iter2/train.jsonl \
  --output_dir ~/.unsloth/studio/outputs/chaosnexus-tuned-iter2-rocm
```

**Checkpoint (fill after train):** `/home/flyingmongoose/.unsloth/studio/outputs/chaosnexus-tuned-iter2-rocm` (ROCm PEFT, 2 epochs, train_loss≈0.84)

## Eval

```bash
HIP_VISIBLE_DEVICES=0 ~/.unsloth/studio/unsloth_studio/bin/python scripts/run_evals.py \
  --model ~/.unsloth/studio/outputs/chaosnexus-tuned-iter2-rocm \
  --max_tokens 1024 \
  --indices 1,4,5,7 \
  --output tests/eval_results_iter2_smoke.md

HIP_VISIBLE_DEVICES=0 ~/.unsloth/studio/unsloth_studio/bin/python scripts/run_evals.py \
  --model ~/.unsloth/studio/outputs/chaosnexus-tuned-iter2-rocm \
  --max_tokens 1024 \
  --output tests/eval_results_iter2.md
```

Score → `tests/eval_scores_iter2.md`.

## Iter-2 result (2026-07-24)

- Mean **0.472**; smoke Fail on prompt 1 (`<tool_call>` spam).
- **Hold** HF + announce (below 0.90 publish gate and below 0.70 alpha bar).
- Checkpoint kept at path above for comparison; do not Hub-publish.

## Iter-3 outline

1. Train on curated goldens only (exclude augmented tool-call ShareGPT residue).
2. Exact signatures: `db_connect(id, "sqlite://…")`, `base64_encode`, `register_cvar`/`get_cvar`, `create_timer`.
3. Anti-invention coverage for `fs_data_*`, `regex_find_all`, `to_base64`, `cn_a_sqlite_*`, `emit`.
4. Eval with `do_sample=False` for stable scoring; keep `--max_tokens 1024`.
