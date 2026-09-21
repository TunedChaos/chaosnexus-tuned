# chaosnexus-tuned/scripts/run_v1_benchmarks.sh
#!/usr/bin/env bash
# Reproduce ChaosNexus Tuned v1 Anvil benchmarks (primary HF eval).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PYTHON="${CHAOSNEXUS_PYTHON:-$HOME/.unsloth/studio/unsloth_studio/bin/python}"
MODEL="${CHAOSNEXUS_V1_MODEL:-$HOME/.unsloth/studio/outputs/ChaosNexus_Tuned_v1}"
ANVIL_ONLY=0

for arg in "$@"; do
  case "$arg" in
    --anvil-only) ANVIL_ONLY=1 ;;
    --help|-h)
      echo "Usage: $0 [--anvil-only]"
      echo "  Runs greedy Anvil smoke + full 18 against ChaosNexus_Tuned_v1."
      echo "  Optional Open-LLM lm_eval is documented in launch/model/ChaosNexus_Tuned_v1/BENCHMARKS.md"
      exit 0
      ;;
  esac
done

if [[ ! -d "$MODEL" ]]; then
  echo "Missing model dir: $MODEL" >&2
  echo "Create alias: ln -sfn ~/.unsloth/studio/outputs/chaosnexus-tuned-iter8-rocm ~/.unsloth/studio/outputs/ChaosNexus_Tuned_v1" >&2
  exit 1
fi

export HIP_VISIBLE_DEVICES="${HIP_VISIBLE_DEVICES:-0}"

echo "==> Anvil smoke (1,4,5,7) on $MODEL"
"$PYTHON" scripts/run_evals.py \
  --model "$MODEL" \
  --max_tokens 1024 --greedy --indices 1,4,5,7 \
  --output tests/eval/eval_results_v1_smoke.md

echo "==> Anvil full 18"
"$PYTHON" scripts/run_evals.py \
  --model "$MODEL" \
  --max_tokens 1024 --greedy \
  --output tests/eval/eval_results_v1.md

echo "Done. Score against tests/eval/eval_scores_v1.md (Pass=1 / Partial=0.5 / Fail=0)."
if [[ "$ANVIL_ONLY" -eq 0 ]]; then
  echo "For optional lm_eval setup, see ../launch/model/ChaosNexus_Tuned_v1/BENCHMARKS.md"
fi
