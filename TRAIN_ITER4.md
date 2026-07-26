# chaosnexus-tuned/TRAIN_ITER4.md

# Train iteration-4 plan (post iter-3 hold; no Codex)

**Trigger:** Iteration-3 mean **0.556** (&lt;0.70); smoke clear. Codex MCP deferred until ≥0.70.  
**Gates (dual):** alpha ≥0.70; full-version ≥0.90.  
**Public:** Codeberg sync paused (`.forgejo/workflows/codeberg-sync.yml.disabled`); polyrepos reorphaned to initial commit.

## Dataset

- Injector: `scripts/injectors/inject_iter4_api_goldens.py`
- Output: `datasets/iter4/train.jsonl`
- Goldens-only + priority upsample for fails 6/9/10/12/13; no augmented ShareGPT; no Codex

```bash
cd chaosnexus-tuned && python scripts/injectors/inject_iter4_api_goldens.py
```

## Train

```bash
cd chaosnexus-tuned
HIP_VISIBLE_DEVICES=0 ~/.unsloth/studio/unsloth_studio/bin/python train_peft_rocm.py \
  --dataset datasets/iter4/train.jsonl \
  --output_dir ~/.unsloth/studio/outputs/chaosnexus-tuned-iter4-rocm
```

**Checkpoint (fill after train):** `/home/flyingmongoose/.unsloth/studio/outputs/chaosnexus-tuned-iter4-rocm` (ROCm PEFT, 2 epochs, train_loss≈0.089)

## Eval (greedy)

```bash
HIP_VISIBLE_DEVICES=0 ~/.unsloth/studio/unsloth_studio/bin/python scripts/run_evals.py \
  --model ~/.unsloth/studio/outputs/chaosnexus-tuned-iter4-rocm \
  --max_tokens 1024 --greedy --indices 1,4,5,7 \
  --output tests/eval_results_iter4_smoke.md

HIP_VISIBLE_DEVICES=0 ~/.unsloth/studio/unsloth_studio/bin/python scripts/run_evals.py \
  --model ~/.unsloth/studio/outputs/chaosnexus-tuned-iter4-rocm \
  --max_tokens 1024 --greedy \
  --output tests/eval_results_iter4.md
```

Score → `tests/eval_scores_iter4.md`.

## Iter-4 result (2026-07-24)

- Mean **0.389** (regression vs iter-3 **0.556**); smoke Fail on prompt 4 (`sqlite_*` invent).
- **Hold** HF + announce. Codex still deferred.
- Likely cause: oversized priority upsample → ban-list mode collapse. Iter-5: smaller corpus, more positive exemplars (see `tests/eval_scores_iter4.md`).
