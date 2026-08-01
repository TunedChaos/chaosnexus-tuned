# chaosnexus-tuned/tests/eval_scores_iter6.md

# Iteration-6 Anvil eval scores (2026-07-24)

**Checkpoint:** `/home/flyingmongoose/.unsloth/studio/outputs/chaosnexus-tuned-iter6-rocm`  
**Train:** ROCm PEFT SFT, 840 rows (base×20 + focus 4/6/8/17×40), 2 epochs, train_loss≈0.384  
**Decode:** greedy (`do_sample=False`)  
**Raw:** `tests/eval_results_iter6_smoke.md`, `tests/eval_results_iter6.md`  
**Codex:** deferred  
**Prior:** iter-5 mean 0.722 / smoke Fail

## Smoke (1 / 4 / 5 / 7)

| # | Score | Notes |
|---|-------|-------|
| 1 | Partial | `http_get`/`from_json` OK; invented `http_get_status` |
| 4 | Pass | Exact `db_connect`/`db_query` + TOML |
| 5 | Pass | Crypto + KV |
| 7 | Pass | `shell=["curl"]` + `run_command` |

**Smoke gate:** CLEAR (no Fail on the four).

## Full 18

| # | Score | Notes |
|---|-------|-------|
| 1 | 0.5 | Real HTTP; `http_get_status` invent |
| 2 | 0.5 | Correct FS hosts; awkward extension check |
| 3 | 1.0 | Fibonacci |
| 4 | 1.0 | Native SQLite |
| 5 | 1.0 | Crypto + KV |
| 6 | 1.0 | `regex_match` + `json_extract` |
| 7 | 0.5 | Full-run preferred `npx`+curl; smoke used correct curl |
| 8 | 0.5 | `cn_a_install_plugin` OK; thin Forge narrative |
| 9 | 1.0 | Events |
| 10 | 1.0 | Timer + KV + events |
| 11 | 1.0 | MCP client |
| 12 | 0.0 | Invented `down_mcp_*` |
| 13 | 1.0 | `sys_os` |
| 14 | 1.0 | Watchdog |
| 15 | 1.0 | CVars |
| 16 | 1.0 | `load_config` |
| 17 | 1.0 | `ws_connect(url, cb)` |
| 18 | 1.0 | `fs_data_*` |

**Sum:** 15.0 / 18  
**Mean:** **0.833**

## Gate decision

**ALPHA GATE PASS.** Mean ≥0.70 **and** smoke clear.  
**Full-version (≥0.90):** not yet (0.833).  
**HF + Variant A announce:** unblocked for alpha (Codex still deferred until optional PoC).  
Do not claim “full version.” Remaining nits: prompts 1/2/7/8/12.

### Next

1. Finalize model card + upload adapter to Hugging Face (alpha).
2. Variant A posts per `launch/POSTING_ORDER.md` after Hub URL exists.
3. Optional iter-7 polish for 0.90 / prompt 12 before “full” claim.
4. Re-enable Codeberg sync only when intentionally publishing public tree updates.
