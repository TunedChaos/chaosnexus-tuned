# chaosnexus-tuned/tests/eval_scores_iter4.md

# Iteration-4 Anvil eval scores (2026-07-24)

**Checkpoint:** `/home/flyingmongoose/.unsloth/studio/outputs/chaosnexus-tuned-iter4-rocm`  
**Train:** ROCm PEFT SFT, goldens-only + priority upsample (5040 rows), 2 epochs, train_loss≈0.089  
**Decode:** greedy (`do_sample=False`)  
**Raw:** `tests/eval_results_iter4_smoke.md`, `tests/eval_results_iter4.md`  
**Codex:** deferred (not used)

## Smoke (1 / 4 / 5 / 7)

| # | Score | Notes |
|---|-------|-------|
| 1 | Pass | Clean `http_get`/`from_json` |
| 4 | Fail | Reinvented `sqlite_connect`/`sqlite_query` (regression vs iter-3 Pass) |
| 5 | Pass | Crypto + KV exact |
| 7 | Partial | Correct shell TOML; invented `curl()` instead of `run_command` |

**Smoke gate:** FAIL (prompt 4 Fail).

## Full 18

| # | Score | Notes |
|---|-------|-------|
| 1 | 1.0 | Clean HTTP |
| 2 | 0.0 | Invented `walk_dir` |
| 3 | 0.0 | No Fibonacci script; dumped API ban-list |
| 4 | 0.0 | Invented SQLite aliases |
| 5 | 1.0 | Crypto + KV |
| 6 | 0.5 | `json_extract` OK; invented `regex_find_all` |
| 7 | 0.5 | TOML OK; invented `curl()` |
| 8 | 0.0 | Kept `chaoswrench_install_plugin` |
| 9 | 0.5 | Event signatures OK; `JSON::to_string` invent |
| 10 | 0.0 | Invented `npx_chaosnexus_anvil_*` |
| 11 | 1.0 | `mcp_connect` + `mcp_call_tool` |
| 12 | 0.0 | Wrong MCP hop / `mcp_call` |
| 13 | 0.0 | Invented `os_name`/`os_version` |
| 14 | 0.5 | Timer/`sys_os` OK; Result-style invent |
| 15 | 0.0 | Invented `con_var_*` |
| 16 | 0.5 | `load_config` OK; invented `cv_set` |
| 17 | 1.0 | `ws_connect` OK |
| 18 | 0.5 | `fs_data_*` OK; TOML nesting nit |

**Sum:** 7.0 / 18  
**Mean:** **0.389** (need ≥0.70; **regression** vs iter-3 0.556)

## Gate decision

**HOLD.** Smoke Fail; mean below 0.70 and below iter-3. Do not publish HF. Do not announce. Codex stays deferred.

### Likely cause

Heavy priority upsample (5040 near-duplicate anti-invention rows) drove low train loss (~0.09) but **mode collapse**: the model regurgitates ban-lists and invents alternate wrong names (`sqlite_*`, `walk_dir`, `con_var_*`, `npx_*`) instead of the gold scripts.

### Iter-5 outline

1. Shrink corpus: fewer unique goldens, milder upsample (target ~500–1000 rows, not 5k clones).
2. Prefer positive exemplar density over long "never invent X" lists in assistant turns.
3. Restore prompt-4 / prompt-3 / CVar goldens that were Pass in iter-3.
4. Keep greedy eval; compare against iter-3 checkpoint as regression baseline.
