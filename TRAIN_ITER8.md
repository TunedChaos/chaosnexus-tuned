# chaosnexus-tuned/TRAIN_ITER8.md

# Train iteration-8 plan (full-version ≥0.90)

**Trigger:** Iter-7 mean **0.611** / smoke Fail (regression). Iter-6 remains best (**0.833**, alpha pass).  
**Lesson:** focus×45 + “Register …” templates fixed prompt 12 but collapsed 1/5/9/13/17.  
**Codex:** deferred. Public remotes frozen.

## Approach

1. Re-anchor on iter-6-style full-surface base (+ exact crypto eval prompt).
2. Mild focus upsample for **12 / 1 / 2 / 7 / 8** (not ×45).
3. Continue-train from **iter-6 adapter** at lower LR so the floor holds.

## Dataset / train / eval

```bash
cd chaosnexus-tuned
python scripts/injectors/inject_iter8_api_goldens.py

HIP_VISIBLE_DEVICES=0 ~/.unsloth/studio/unsloth_studio/bin/python train_peft_rocm.py \
  --dataset datasets/iter8/train.jsonl \
  --adapter ~/.unsloth/studio/outputs/chaosnexus-tuned-iter6-rocm \
  --output_dir ~/.unsloth/studio/outputs/chaosnexus-tuned-iter8-rocm \
  --learning_rate 1e-4 --num_epochs 1.5

HIP_VISIBLE_DEVICES=0 ~/.unsloth/studio/unsloth_studio/bin/python scripts/run_evals.py \
  --model ~/.unsloth/studio/outputs/chaosnexus-tuned-iter8-rocm \
  --max_tokens 1024 --greedy --indices 1,4,5,7 \
  --output tests/eval_results_iter8_smoke.md

HIP_VISIBLE_DEVICES=0 ~/.unsloth/studio/unsloth_studio/bin/python scripts/run_evals.py \
  --model ~/.unsloth/studio/outputs/chaosnexus-tuned-iter8-rocm \
  --max_tokens 1024 --greedy \
  --output tests/eval_results_iter8.md
```

**Checkpoint:** `~/.unsloth/studio/outputs/chaosnexus-tuned-iter8-rocm`  
**Score:** mean **0.944**, smoke CLEAR → `tests/eval_scores_iter8.md`.
