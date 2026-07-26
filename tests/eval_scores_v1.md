# chaosnexus-tuned/tests/eval_scores_v1.md

# ChaosNexus Tuned v1 - Anvil eval scores (2026-07-24)

**Release:** ChaosNexus Tuned v1 (`ChaosNexus_Tuned_v1`)  
**Checkpoint:** `~/.unsloth/studio/outputs/ChaosNexus_Tuned_v1` (alias of `chaosnexus-tuned-iter8-rocm`)  
**Train lineage:** iter-5 → iter-6 (alpha 0.833) → iter-8 continue-train (this release)  
**Decode:** greedy (`do_sample=False`)  
**Raw:** `tests/eval_results_iter8_smoke.md`, `tests/eval_results_iter8.md`  
**Hub card:** `launch/model/ChaosNexus_Tuned_v1/README.md`

This file is the **canonical score sheet** for the v1 publication. Numbers match `eval_scores_iter8.md`.

## Smoke (1 / 4 / 5 / 7)

| # | Score | Notes |
|---|-------|-------|
| 1 | Pass | `http_get` + `from_json` only (no invents) |
| 4 | Pass | `db_connect` / `db_query` + TOML |
| 5 | Pass | `sha256` + `base64_encode` + KV |
| 7 | Pass | `shell=["curl"]` + `run_command` |

**Smoke gate:** CLEAR.

## Full 18

| # | Score | Notes |
|---|-------|-------|
| 1 | 1.0 | Real HTTP; no `http_get_status` |
| 2 | 1.0 | `ends_with` + consolidated `ports_found.txt` |
| 3 | 1.0 | Fibonacci |
| 4 | 1.0 | Native SQLite |
| 5 | 1.0 | Crypto + KV |
| 6 | 1.0 | `regex_match` + `json_extract` |
| 7 | 1.0 | Curl allowlist (not npx) |
| 8 | 1.0 | `cn_a_install_plugin` + Forge Pending narrative |
| 9 | 1.0 | Events (script correct; prose wrongly denies `create_event`) |
| 10 | 1.0 | Timer + KV + events |
| 11 | 1.0 | MCP client |
| 12 | 1.0 | `register_mcp_tool` + `mcp_connect` / `mcp_call_tool` (no `down_mcp_*`) |
| 13 | 1.0 | `sys_os` |
| 14 | 0.5 | Watchdog intent OK; invalid Rhai `if let Ok(...)` |
| 15 | 1.0 | CVars |
| 16 | 1.0 | `load_config` |
| 17 | 1.0 | `ws_connect(url, cb)` |
| 18 | 0.5 | `fs_data_write` OK; weak / wrong A/B permission TOML |

**Sum:** 17.0 / 18  
**Mean:** **0.944**

## Gate decision

**FULL-VERSION GATE PASS** (mean ≥0.90 and smoke clear). Ready for Hugging Face upload as `ChaosNexus_Tuned_v1` when confirmed.
