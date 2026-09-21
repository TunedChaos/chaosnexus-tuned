# chaosnexus-tuned/TRAIN_ITER3.md

# Train iteration-3 plan (post iter-2 hold)

**Trigger:** Iteration-2 mean **0.472** (&lt;0.70 alpha / &lt;0.90 full); smoke Fail on prompt 1 (`&lt;tool_call&gt;` spam).  
**Gates (dual):** alpha publish ≥0.70; full-version claim ≥0.90; hold if &lt;0.70.

## Dataset (goldens-only)

- Injector: `scripts/injectors/inject_iter3_api_goldens.py`
- Output: `datasets/iter3/train.jsonl` (+ `build_meta.json`)
- **No augmented ShareGPT merge** (drops tool-call / invented-API residue)
- Exact Anvil signatures from Rust bindings (`create_timer(ms, repeat, cb, payload)`, string event/WS callbacks, `base64_encode`, real `fs_data_*`, `cn_a_install_plugin`, `[plugins.*.permissions]`)
- Studio YAML: `unsloth_training/ChaosNexus_Tuned.yaml` → `dataset_path: datasets/iter3/train.jsonl`

```bash
cd chaosnexus-tuned
python scripts/injectors/inject_iter3_api_goldens.py
```

## Train

```bash
cd chaosnexus-tuned
HIP_VISIBLE_DEVICES=0 ~/.unsloth/studio/unsloth_studio/bin/python train_peft_rocm.py \
  --dataset datasets/iter3/train.jsonl \
  --output_dir ~/.unsloth/studio/outputs/chaosnexus-tuned-iter3-rocm
```

**Checkpoint (fill after train):** `/home/flyingmongoose/.unsloth/studio/outputs/chaosnexus-tuned-iter3-rocm` (ROCm PEFT, 2 epochs, train_loss≈0.219)

## Eval (greedy)

```bash
HIP_VISIBLE_DEVICES=0 ~/.unsloth/studio/unsloth_studio/bin/python scripts/run_evals.py \
  --model ~/.unsloth/studio/outputs/chaosnexus-tuned-iter3-rocm \
  --max_tokens 1024 --greedy \
  --indices 1,4,5,7 \
  --output tests/eval_results_iter3_smoke.md

HIP_VISIBLE_DEVICES=0 ~/.unsloth/studio/unsloth_studio/bin/python scripts/run_evals.py \
  --model ~/.unsloth/studio/outputs/chaosnexus-tuned-iter3-rocm \
  --max_tokens 1024 --greedy \
  --output tests/eval_results_iter3.md
```

Score → `tests/eval_scores_iter3.md`.

## Iter-3 result (2026-07-24)

- Mean **0.556**; smoke **CLEAR** (1 Partial, 4/5/7 Pass).
- **Hold** HF + announce (below 0.70 alpha / 0.90 full).
- Checkpoint kept at path above; do not Hub-publish.
- Next: harden goldens on fails 6/9/10/12/13 (see `tests/eval_scores_iter3.md`).
