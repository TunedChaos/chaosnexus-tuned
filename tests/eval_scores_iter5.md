# chaosnexus-tuned/tests/eval_scores_iter5.md

# Iteration-5 Anvil eval scores (2026-07-24)

**Checkpoint:** `/home/flyingmongoose/.unsloth/studio/outputs/chaosnexus-tuned-iter5-rocm`  
**Train:** ROCm PEFT SFT, 25×28=700 positive goldens, 2 epochs, train_loss≈0.431  
**Decode:** greedy (`do_sample=False`)  
**Raw:** `tests/eval_results_iter5_smoke.md`, `tests/eval_results_iter5.md`  
**Codex:** deferred  
**Baseline:** iter-3 mean 0.556 / iter-4 mean 0.389

## Smoke (1 / 4 / 5 / 7)

| # | Score | Notes |
|---|-------|-------|
| 1 | Partial | `http_get`/`from_json` OK; invented `body.status` |
| 4 | Fail | Invented `sqlite_connect` / method-style `.query` (smoke blocker) |
| 5 | Pass | `sha256`/`base64_encode`/`kv_*` |
| 7 | Pass | Shell TOML + `run_command("curl", …)` |

**Smoke gate:** FAIL (prompt 4 Fail).

## Full 18

| # | Score | Notes |
|---|-------|-------|
| 1 | 0.5 | Real HTTP; field invent |
| 2 | 1.0 | `list_dir`/`fs_read`/`write_file_string` |
| 3 | 1.0 | Fibonacci |
| 4 | 0.0 | Wrong SQLite surface |
| 5 | 1.0 | Crypto + KV |
| 6 | 0.0 | Invented `regex`/`regex_matches` helpers |
| 7 | 1.0 | Deny-by-default curl |
| 8 | 0.0 | `chaoswrench_install_plugin` kept |
| 9 | 1.0 | Event bus exact |
| 10 | 1.0 | Timer + KV + events |
| 11 | 1.0 | MCP client |
| 12 | 1.0 | MCP router hop |
| 13 | 1.0 | `sys_os` |
| 14 | 0.5 | Timer/`sys_os` OK; Result invent |
| 15 | 1.0 | `register_cvar`/`get_cvar` |
| 16 | 1.0 | `load_config` + CVar |
| 17 | 0.0 | Wrong `ws_connect` arity / `ws_send` invent |
| 18 | 1.0 | `fs_data_*` + capabilities |

**Sum:** 13.0 / 18  
**Mean:** **0.722** (clears ≥0.70 numeric bar; **above** iter-3 0.556)

## Gate decision

**HOLD announce/HF** until smoke clears (prompt 4 Fail). Numeric mean ≥0.70 is encouraging; do not claim alpha publish while smoke Fail remains. Codex still deferred.

### Iter-6 tighten (minimal)

1. Heavy upsample **only** prompt-4 `db_connect`/`db_query` positive + anti-`sqlite_*` pairs.
2. Fix 6 (`regex_match` array), 8 (`cn_a_install_plugin`), 17 (`ws_connect(url, cb)`).
3. Keep corpus small (~700–1000); do not return to iter-4 ban-list collapse.
