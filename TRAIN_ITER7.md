# chaosnexus-tuned/TRAIN_ITER7.md

# Train iteration-7 plan (full-version ≥0.90) — COMPLETED / REGRESSED

**Result:** mean **0.611**, smoke **FAIL**. See `tests/eval_scores_iter7.md`.  
**Cause:** focus×45 + “Register …” assistant templates fixed prompt 12 but collapsed 1/5/9/13/17.  
**Follow-up:** `TRAIN_ITER8.md` (continue from iter-6 adapter).

## Commands used

```bash
cd chaosnexus-tuned
python scripts/injectors/inject_iter7_api_goldens.py

HIP_VISIBLE_DEVICES=0 ~/.unsloth/studio/unsloth_studio/bin/python train_peft_rocm.py \
  --dataset datasets/iter7/train.jsonl \
  --output_dir ~/.unsloth/studio/outputs/chaosnexus-tuned-iter7-rocm
```

**Checkpoint:** `~/.unsloth/studio/outputs/chaosnexus-tuned-iter7-rocm` (do not ship).
