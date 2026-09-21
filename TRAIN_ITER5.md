# chaosnexus-tuned/TRAIN_ITER5.md

# Train iteration-5 plan (post iter-4 regression)

**Trigger:** Iteration-4 mean **0.389** (regression vs iter-3 **0.556**); smoke Fail; ban-list mode collapse.  
**Gates:** alpha ≥0.70; full-version ≥0.90. Codex deferred. Public remotes stay frozen.

## Dataset

- Injector: `scripts/injectors/inject_iter5_api_goldens.py`
- Output: `datasets/iter5/train.jsonl` (~25 goldens × 28 ≈ 700 rows)
- Positive exemplars first; short corrections only; no 5k anti-invention clones

```bash
cd chaosnexus-tuned && python scripts/injectors/inject_iter5_api_goldens.py
```

## Train

```bash
cd chaosnexus-tuned
HIP_VISIBLE_DEVICES=0 ~/.unsloth/studio/unsloth_studio/bin/python train_peft_rocm.py \
  --dataset datasets/iter5/train.jsonl \
  --output_dir ~/.unsloth/studio/outputs/chaosnexus-tuned-iter5-rocm
```

**Checkpoint (fill after train):** `/home/flyingmongoose/.unsloth/studio/outputs/chaosnexus-tuned-iter5-rocm` (ROCm PEFT, 2 epochs, train_loss≈0.431)

## Eval (greedy)

```bash
HIP_VISIBLE_DEVICES=0 ~/.unsloth/studio/unsloth_studio/bin/python scripts/run_evals.py \
  --model ~/.unsloth/studio/outputs/chaosnexus-tuned-iter5-rocm \
  --max_tokens 1024 --greedy --indices 1,4,5,7 \
  --output tests/eval_results_iter5_smoke.md

HIP_VISIBLE_DEVICES=0 ~/.unsloth/studio/unsloth_studio/bin/python scripts/run_evals.py \
  --model ~/.unsloth/studio/outputs/chaosnexus-tuned-iter5-rocm \
  --max_tokens 1024 --greedy \
  --output tests/eval_results_iter5.md
```

Score → `tests/eval_scores_iter5.md`. Compare to iter-3 mean 0.556 as regression floor.

## Iter-5 result (2026-07-24)

- Mean **0.722** (clears numeric ≥0.70; beats iter-3 **0.556** / iter-4 **0.389**).
- Smoke **Fail** on prompt 4 (`sqlite_connect` invent) → **hold** HF/announce until smoke clears.
- Codex still deferred. Iter-6: focus prompt 4/6/8/17 only.
