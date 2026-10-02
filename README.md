# agentdojo-ja

Japanese localization of [AgentDojo](https://github.com/ethz-spylab/agentdojo) (MIT) suites. **Unofficial community
extension**; not affiliated with the AgentDojo authors. A derivative work: see `NOTICE.md` (attribution, which files derive from upstream) and `LICENSE`. Please cite AgentDojo (Debenedetti et al., NeurIPS D&B 2024) when using this. **v0.2.0: all four upstream suites** (`banking`, `slack`, `travel`, `workspace`) with the same task counts as upstream v1.2.2 (97 user / 31 injection tasks, same IDs).

Localization, not translation: yen amounts, 全銀-style accounts, 消費税, 家賃, Japanese file names/addresses, and
Japanese-specific attacks (keigo, fake 【システム】 notices, half-width-kana channel, script transforms).
Everything is fictional (no real banks/accounts/addresses).

## Use

```bash
uv venv --python 3.11 && uv pip install -e ../agentdojo -e . pytest
.venv/bin/python -m pytest tests                                    # 43 tests: counts vs upstream, ground truth, injectability, no-op, normalization
.venv/bin/python -m agentdojo.scripts.check_suites -ml agentdojo_ja -v v1.2.2-ja --no-check-injectable
# run (OpenAI-compatible endpoint, e.g. mlx_lm.server; or --local-harmony for llm-jp-4.x in-process)
OPENAI_COMPATIBLE_BASE_URL=http://127.0.0.1:8089/v1 OPENAI_COMPATIBLE_API_KEY=local \
  .venv/bin/python -m agentdojo_ja.run --model-id <id> --language ja --attack ja_keigo
```

## Preliminary numbers (Qwen3.5-4B 4bit, utility only, no attack; sanity check of the pipeline, not a benchmark result)

| Suite | Utility |
|---|---|
| English `banking` (upstream) | 12/16 |
| `banking_ja` | 5/16 (6/16 with upstream's escaped tool output) |

Most Japanese failures are turns that announce a tool call ("取引明細を取得します") and stop without calling it, so this mainly reflects the small model's Japanese tool use. llm-jp-4.1-8b-thinking (4bit, in-process) ran out of its 3,000-token budget while thinking on the two tasks tried; a stronger model is needed before comparing languages.

## What is here

| Piece | Purpose |
|---|---|
| `suites/banking_ja` | 16 user / 9 injection tasks, aligned 1:1 with upstream `banking` |
| `suites/slack_ja` | 21 user / 5 injection tasks |
| `suites/travel_ja` | 20 user / 7 injection tasks (cities, yen prices, 和食/中華…) |
| `suites/workspace_ja` | 40 user / 14 injection tasks (山田 花子 @ 青雀テック; mail, calendar, drive; 沖縄 instead of Hawaii) |
| | all state-based utility/security; fictional data; generators in `scripts/` |
| `normalize.py` | NFKC / 全角半角 / kanji numerals (千五十円) / address normalization for checks |
| `attacks.py`, `transforms.py` | 25 registered attacks: `ja_important_instructions`, `ja_keigo`, `ja_system_bracket`, `ja_channel_aware`, and `base+transform` variants |
| `pipeline.py` | tool-output formatters that keep Japanese (see below) |
| `local_llm.py` | in-process MLX backend that parses llm-jp's harmony tool calls |

## Findings so far (candidates for upstream issues)

1. **Tool output is `\uXXXX`-escaped for non-ASCII.** `tool_result_to_str` uses `yaml.safe_dump` / `json.dumps` with
   default ASCII escaping, so a Japanese tool result reaches the model as `"普通"`. Fix: `allow_unicode=True` / `ensure_ascii=False`. Measured effect on a 4B model (Qwen3.5-4B 4bit, 16 tasks, no attack): 6/16 escaped vs 5/16 unescaped, i.e. no measurable difference at this scale (n=16, weak model); the unrealism stands, the size of the effect on stronger models is open.
2. **`TaskSuite.check()` reports every user task "not injectable"** (also for upstream's own English suites at v0.1.35):
   `is_task_injectable` skips tool messages whose content is a list of blocks.
3. **Raw injection text is formatted into the environment YAML source**, so quotes/colons/newlines in an attack string can break it; `JaTaskSuite` substitutes after parsing.
4. **Upstream `workspace` injection_task_6..13 have an empty ground truth**, so upstream's own `check_suites` reports them as unsolved. `workspace_ja` ships working ground truths for them (verified against `security()`).
5. Weak upstream utility checks: `workspace` user_task_27 passes if "0" and "4" appear anywhere in the answer; user_task_25 never checks the recipients. `workspace_ja` uses stricter, notation-insensitive checks.
6. Upstream banking checks: `service or "" in subject` is `service or ("" in subject)` (InjectionTask0/1/3);
   `UserTask5` utility checks 50.00 while its ground truth sends 5.00; `UserTask6` (v1.2.2) is satisfied by the pre-existing Spotify standing order.

To be verified before relying on them: the real interbank (全銀) character set for the 摘要/振込依頼人名 field (half-width kana + alphanumerics) and invoice-number formats.
