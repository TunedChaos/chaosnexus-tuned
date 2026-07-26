# chaosnexus-tuned/tests/eval_scores_iter1.md

# Iteration-1 Anvil eval scores (2026-07-24)

**Checkpoint:** `~/.unsloth/studio/outputs/unsloth_granite-4.1-8b__project-chaosnexus-tuned_1783969119`  
**Runner:** ROCm PEFT overlay via Unsloth studio Python (`scripts/run_evals.py`)  
**Raw outputs:** `tests/eval_results_smoke.md`, `tests/eval_results.md`  
**Prior archive:** `tests/eval_results_prior.md`

## Rubric

Pass=1 / Partial=0.5 / Fail=0. Criteria: Rhai only; real Anvil host APIs; docs-first when unknown; security/allowlists where relevant; looks executable under Anvil.

## Smoke (1 / 4 / 5 / 7)

| # | Score | Notes |
|---|-------|-------|
| 1 | Partial | `http_get` real; invented response shape / no `from_json` |
| 4 | Fail | Invented `sqlite_query`; real APIs are `db_connect` / `db_query` |
| 5 | Fail | Narrative only; no Rhai / no `sha256` / `kv_set` |
| 7 | Partial | Allowlist + `run_command` intent OK; wrong TOML schema/filename |

**Smoke gate:** FAIL (requires all four Pass or Partial; 4 and 5 Fail).

## Full 18

| # | Score | Notes |
|---|-------|-------|
| 1 | 0.5 | Real `http_get`; weak JSON / response typing |
| 2 | 1.0 | `fs_list_dir` / `fs_read` / `fs_write` runnable Rhai |
| 3 | 0.5 | Fib intent; Rust-style iterator APIs not valid Rhai |
| 4 | 0.0 | Invented `sqlite_query` |
| 5 | 0.0 | No script |
| 6 | 0.5 | Invented `regex_find_all` / `parse_json` |
| 7 | 0.5 | Security framing OK; config invent |
| 8 | 1.0 | Install + Forge HITL approval narrative solid |
| 9 | 0.5 | Correct event API names; no code |
| 10 | 0.5 | `kv_*` OK; invented `emit_event`; no code |
| 11 | 0.0 | Denied real `mcp_connect`; HTTP substitute |
| 12 | 0.5 | HTTP router invent; not `register_mcp_tool` / `mcp_*` |
| 13 | 0.5 | Used `uname` via shell instead of `sys_os` |
| 14 | 0.5 | Correct capability names; no script body |
| 15 | 0.0 | Invented `cn_a_` / `cn_v_` |
| 16 | 0.5 | Real `load_config`; invented `set_cvar` |
| 17 | 0.5 | Mentions `ws_connect`; no code |
| 18 | 0.0 | Invented `fs_data_*` / JS-style WS callbacks |

**Sum:** 8.0 / 18  
**Mean:** **0.444** (need ≥0.70)

## Gate decision

**HOLD.** Do not publish HF weights. Do not post Variant A (or Variant B by default). Proceed to train iter-2.

## Failure themes for iter-2 data

1. Exact host fn names from Rhai API page (`sha256`, `kv_set`, `db_*`, `mcp_*`, `register_cvar`, `sys_os`, `regex_match`, `from_json` / `json_extract`, `fs_read` / `fs_write`).
2. Always emit complete Rhai blocks (too many narrative-only truncations at 512 tokens; raise `max_tokens` and train for finish-the-script).
3. Docs-search tool-call habit before inventing APIs (prompt 4).
4. Real `chaoswrench.toml` / plugin permission schema, not invented `Anvil.toml` sections.
5. Pure Rhai idioms (no Rust iterators / JS callbacks).
