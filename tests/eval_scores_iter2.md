# chaosnexus-tuned/tests/eval_scores_iter2.md

# Iteration-2 Anvil eval scores (2026-07-24)

**Checkpoint:** `/home/flyingmongoose/.unsloth/studio/outputs/chaosnexus-tuned-iter2-rocm`  
**Train:** ROCm PEFT SFT, 2 epochs, train_loss≈0.84, dataset `datasets/iter2/train.jsonl`  
**Raw:** `tests/eval_results_iter2_smoke.md`, `tests/eval_results_iter2.md`

## Smoke (1 / 4 / 5 / 7)

| # | Score | Notes |
|---|-------|-------|
| 1 | Fail | Smoke run: `<tool_call>` spam, no usable script (sampling variance; full run Partial) |
| 4 | Partial | `db_connect`/`db_query` named; wrong call shape |
| 5 | Partial | `sha256`/`kv_set`/`kv_get`; invented `to_base64` |
| 7 | Partial | Allowlist intent; prefers `http_get` over requested `curl` + TOML invent |

**Smoke gate:** FAIL (prompt 1 Fail on smoke artifact).

## Full 18

| # | Score | Notes |
|---|-------|-------|
| 1 | 0.5 | `http_get`; invented response fields |
| 2 | 1.0 | `fs_list_dir` / `fs_read` / `fs_write` |
| 3 | 1.0 | Valid Rhai Fibonacci / filter / average |
| 4 | 0.5 | Real DB names; wrong arity |
| 5 | 0.5 | Real crypto/KV names; `to_base64` invent + tool noise |
| 6 | 0.0 | `regex_find_all` invent + tool spam |
| 7 | 0.5 | Security framing; schema invent; `http_get` vs curl |
| 8 | 0.0 | Skipped HITL install path |
| 9 | 1.0 | `create_event` / `hook_event` / `fire_event` |
| 10 | 0.0 | Denies `create_timer`; invents `emit`/`hook` |
| 11 | 0.0 | Wrong `mcp_connect` usage; invents `tools_get` |
| 12 | 0.5 | `register_mcp_tool` then HTTP instead of MCP hop |
| 13 | 0.5 | Shell `uname` instead of `sys_os` |
| 14 | 1.0 | `create_timer` + `sys_os` + `run_command` |
| 15 | 0.0 | Invented `cn_a_sqlite_query` |
| 16 | 0.5 | `load_config` OK; invented `sys_set_cvar` |
| 17 | 0.5 | `ws_connect` OK; invents send/close helpers |
| 18 | 0.0 | Invented `fs_data_write` / `fs_data_read` |

**Sum:** 8.5 / 18  
**Mean:** **0.472** (need ≥0.90 to publish per plan; also below 0.70 alpha bar)

## Gate decision

**HOLD.** Do not publish HF weights. Do not announce. Plan train iter-3:

1. Drop remaining augmented/tool-call corpus from the mix (it still teaches `<tool_call>` loops and `cn_a_sqlite_*`).
2. Train on **curated goldens only** (or goldens + strictly API-clean rows), upsample harder.
3. Fix golden signatures to match Anvil exactly (`db_connect(id, url)`, `base64_encode`, `create_timer`, `register_cvar`/`get_cvar`).
4. Consider lower temperature / greedy eval (`do_sample=False`) for scoring stability.
5. Add refusal examples for invented APIs that still appear (`fs_data_*`, `regex_find_all`, `to_base64`, `emit`).
