# chaosnexus-tuned/TRAIN_ITER6.md

# Train iteration-6 plan (smoke fix after iter-5 0.722)

**Trigger:** Iter-5 mean **0.722** but smoke Fail on prompt 4; also fails 6/8/17.  
**Gates:** alpha ≥0.70 **and** smoke 1/4/5/7 clear. Codex deferred. Public remotes frozen.

## Dataset

- Injector: `scripts/injectors/inject_iter6_api_goldens.py`
- Base positives ×20 + focus (4/6/8/17) ×40
- Still no Codex / no augmented ShareGPT

```bash
cd chaosnexus-tuned && python scripts/injectors/inject_iter6_api_goldens.py
```

## Train

```bash
HIP_VISIBLE_DEVICES=0 ~/.unsloth/studio/unsloth_studio/bin/python train_peft_rocm.py \
  --dataset datasets/iter6/train.jsonl \
  --output_dir ~/.unsloth/studio/outputs/chaosnexus-tuned-iter6-rocm
```

**Checkpoint (fill after train):** `/home/flyingmongoose/.unsloth/studio/outputs/chaosnexus-tuned-iter6-rocm` (ROCm PEFT, 2 epochs, train_loss≈0.384)

## Eval (greedy)

```bash
HIP_VISIBLE_DEVICES=0 ~/.unsloth/studio/unsloth_studio/bin/python scripts/run_evals.py \
  --model ~/.unsloth/studio/outputs/chaosnexus-tuned-iter6-rocm \
  --max_tokens 1024 --greedy --indices 1,4,5,7 \
  --output tests/eval_results_iter6_smoke.md

HIP_VISIBLE_DEVICES=0 ~/.unsloth/studio/unsloth_studio/bin/python scripts/run_evals.py \
  --model ~/.unsloth/studio/outputs/chaosnexus-tuned-iter6-rocm \
  --max_tokens 1024 --greedy \
  --output tests/eval_results_iter6.md
```

Score → `tests/eval_scores_iter6.md`.

## Iter-6 result (2026-07-24)

- Mean **0.833**; smoke **CLEAR**.
- **Alpha gate PASS** (≥0.70 + smoke). Full-version (≥0.90) not yet.
- HF + Variant A announce unblocked; Codex still deferred.
- Next: Hub upload + announce; optional iter-7 for prompt 12 / 0.90.
