# Model Matrix & Benchmark Targets

## ChaosNexus Tuned v1 (shipped eval)

- **Release:** ChaosNexus Tuned v1 (`ChaosNexus_Tuned_v1`)
- **Base:** IBM Granite 4.1-8B-Instruct via `unsloth/granite-4.1-8b`
- **Primary bench:** Anvil 18-prompt rubric mean **0.944** (smoke clear) - see `tests/eval_scores_v1.md`
- **Card:** `../launch/model/ChaosNexus_Tuned_v1/README.md`

## Future local open-weight targets

The following architectures remain targets for Candle / Burn Rust-native fine-tuning and runtime inference in ChaosNexus:

1. **IBM Granite 4.1-8B-Instruct** (Primary - **v1 LoRA published when Hub upload confirms**)
2. **Qwen 3.5-9B-Instruct** (Target for complex multi-step reasoning)
3. **Qwen 3-8B-Instruct** (Target for standard local chat & command parsing)
4. **DeepSeek-R1-Distilled-Qwen-8B** (Target for deep reasoning and code verification)

## Execution Engine

All target models are deployed locally using **Candle** (for GGUF / Quantized Safetensors inference) and fine-tuned using **Burn** native Rust pipelines (adapter train path today: ROCm PEFT / Unsloth studio).

**Default Crucible download:** [`TunedChaos/ChaosNexus_Tuned_v1-GGUF`](https://huggingface.co/TunedChaos/ChaosNexus_Tuned_v1-GGUF) (Q4_K_M), cached at `~/.chaosnexus/crucible/models`. Crucible loads Granite GGUFs via a dedicated Candle path (`granite.*` metadata + scales). PEFT adapter remains at [`TunedChaos/ChaosNexus_Tuned_v1`](https://huggingface.co/TunedChaos/ChaosNexus_Tuned_v1). Export: `tools/launch/export-chaosnexus-tuned-v1-gguf.sh`.
