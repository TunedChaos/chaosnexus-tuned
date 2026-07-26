# chaosnexus-tuned/tests/eval_scores_iter7.md

# Iteration-7 Anvil eval scores (2026-07-24)

**Checkpoint:** `/home/flyingmongoose/.unsloth/studio/outputs/chaosnexus-tuned-iter7-rocm`  
**Train:** ROCm PEFT SFT, 774 rows (keep×18 + focus×45), 2 epochs  
**Decode:** greedy (`do_sample=False`)  
**Raw:** `tests/eval_results_iter7_smoke.md`, `tests/eval_results_iter7.md`  
**Codex:** deferred  
**Prior:** iter-6 mean 0.833 / smoke CLEAR (alpha pass)

## Smoke (1 / 4 / 5 / 7)

| # | Score | Notes |
|---|-------|-------|
| 1 | Fail | Invented `router_ping_status` / `router_ping_body` (focus bleed from prompt 12) |
| 4 | Pass | `db_connect` / `db_query` |
| 5 | Fail | Template stub only (`register_tool` / `call_tool`); no `sha256` / KV |
| 7 | Partial | Prefers `http_get` over requested `curl` allowlist |

**Smoke gate:** FAIL (1 and 5 Fail).

## Full 18

| # | Score | Notes |
|---|-------|-------|
| 1 | 0.0 | Wrong HTTP hosts (`router_ping_*`) |
| 2 | 0.5 | Real FS hosts; awkward append vs consolidated write |
| 3 | 1.0 | Fibonacci OK despite preamble noise |
| 4 | 1.0 | Native SQLite |
| 5 | 0.0 | No crypto / KV |
| 6 | 1.0 | `regex_match_all` + JSON path intent |
| 7 | 0.5 | Curl allowlist mentioned; prefers HTTP |
| 8 | 1.0 | `cn_a_install_plugin` + Forge Pending |
| 9 | 0.0 | Narrative only; no Rhai |
| 10 | 1.0 | Timer + KV + events |
| 11 | 0.5 | Thin `mcp_connect` sketch |
| 12 | 1.0 | `register_mcp_tool` + `mcp_connect` / `mcp_call_tool` (no `down_mcp_*`) |
| 13 | 0.0 | Meta instruction; no `sys_os` script |
| 14 | 1.0 | Watchdog |
| 15 | 1.0 | CVars |
| 16 | 1.0 | `load_config` |
| 17 | 0.0 | Contradictory WS narrative; no code |
| 18 | 0.5 | Partial A/B permissions + WS write |

**Sum:** 11.0 / 18  
**Mean:** **0.611**

## Gate decision

**REGRESSION.** Mean below alpha floor; smoke Fail. Prompt 12 fixed (+1.0) but oversampling focus (×45) plus “Register …” templates collapsed Passes (5/9/13/17) and polluted prompt 1.

### Next (iter-8)

1. Re-anchor on **iter-6 base goldens** (floor that hit 0.833).
2. Milder focus upsample for **12 / 1 / 2 / 7 / 8**; reinforce exact crypto / events / `sys_os` / WS scripts.
3. Prefer continue-train from **iter-6 adapter** or fresh train with balanced mix (no ×45 focus).
4. Do not claim full-version until mean ≥0.90 **and** smoke clear.
