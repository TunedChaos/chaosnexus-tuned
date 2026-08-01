# chaosnexus-tuned/tests/eval_scores_iter3.md

# Iteration-3 Anvil eval scores (2026-07-24)

**Checkpoint:** `/home/flyingmongoose/.unsloth/studio/outputs/chaosnexus-tuned-iter3-rocm`  
**Train:** ROCm PEFT SFT, goldens-only (25×40=1000), 2 epochs, train_loss≈0.219  
**Decode:** greedy (`do_sample=False`)  
**Raw:** `tests/eval_results_iter3_smoke.md`, `tests/eval_results_iter3.md`

## Smoke (1 / 4 / 5 / 7)

| # | Score | Notes |
|---|-------|-------|
| 1 | Partial | `http_get`/`from_json` present; broken wrapper / invented `fetch` |
| 4 | Pass | `db_connect`/`db_query` + real `[plugins.*.permissions]` |
| 5 | Pass | `sha256`/`base64_encode`/`kv_set`/`kv_get` |
| 7 | Pass | `shell = ["curl"]` + `run_command` |

**Smoke gate:** CLEAR (no total Fail on the four).

## Full 18

| # | Score | Notes |
|---|-------|-------|
| 1 | 0.5 | Real HTTP hosts; broken syntax / field invent |
| 2 | 0.5 | `list_dir` OK; invented `read_file`/`write_file` |
| 3 | 1.0 | Valid Fibonacci / filter / average Rhai |
| 4 | 1.0 | Docs-first native DB |
| 5 | 1.0 | Crypto + KV exact |
| 6 | 0.0 | Invented `regex_find_all`; rejects `json_extract` |
| 7 | 1.0 | Deny-by-default curl path |
| 8 | 0.5 | HITL narrative; still `chaoswrench_install_plugin` not `cn_a_install_plugin` |
| 9 | 0.0 | Wrong `hook_event` / closure invent |
| 10 | 0.0 | Invented `emit_event` / `execute_timer` / `register_event_handler` |
| 11 | 0.5 | `mcp_connect` OK; invented `mcp_call` |
| 12 | 0.0 | Broken downstream MCP hop |
| 13 | 0.0 | Invented `system_os` |
| 14 | 0.5 | Timer/`sys_os` OK; Result-style invent on `run_command` |
| 15 | 1.0 | `register_cvar`/`get_cvar` |
| 16 | 1.0 | `load_config` + CVar fallback |
| 17 | 1.0 | `ws_connect` + allowlist |
| 18 | 0.5 | Real `fs_data_*`; invented `fs_shared` TOML keys |

**Sum:** 10.0 / 18  
**Mean:** **0.556** (need ≥0.70 alpha / ≥0.90 full)

## Gate decision

**HOLD.** Smoke cleared, but mean below 0.70 alpha bar. Do not publish HF weights. Do not announce.

### Iter-4 tighten targets

1. Upsample / hard-negative pairs for prompts **6, 9, 10, 12, 13** (regex, events/timers, MCP hop, `sys_os`).
2. Force `fs_read` / `write_file_string` wording for prompt 2; ban `read_file`/`write_file`.
3. Strengthen `cn_a_install_plugin` vs `chaoswrench_install_plugin`.
4. Keep goldens-only; consider 3 epochs or slightly higher LR only if loss plateaus early.
5. Keep greedy eval for score stability.
