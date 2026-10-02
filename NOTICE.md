# NOTICE

agentdojo-ja is an **unofficial community extension** and is not affiliated with, endorsed by, or maintained by the
AgentDojo authors or ETH Zurich SPY Lab.

It is a derivative work of [AgentDojo](https://github.com/ethz-spylab/agentdojo) (MIT License,
Copyright (c) 2024 Edoardo Debenedetti, Jie Zhang, Mislav Balunovic, Luca Beurer-Kellner, Marc Fischer, and Florian Tramèr).
The following parts adapt upstream code or structure and keep upstream's copyright notice (see `LICENSE`):

| Here | Derived from upstream |
|---|---|
| `src/agentdojo_ja/tools/banking_ja.py` | `default_suites/v1/tools/banking_client.py`, `file_reader.py`, `user_account.py` |
| `src/agentdojo_ja/suites/banking_ja/user_tasks.py` | `default_suites/v1/banking/user_tasks.py` (task intents, ground-truth structure, numbering) |
| `src/agentdojo_ja/suites/banking_ja/injection_tasks.py` | `default_suites/v1/banking/injection_tasks.py` |
| `src/agentdojo_ja/data/banking_ja/*.yaml` | `data/suites/banking/*.yaml` (structure) |
| `src/agentdojo_ja/tools/{slack,email,calendar,travel,drive}_ja.py` | `default_suites/v1/tools/{slack,email_client,calendar_client,travel_booking_client,cloud_drive_client}.py` (data models reused; descriptions/messages localized) |
| `src/agentdojo_ja/suites/{slack,travel,workspace}_ja/*` | `default_suites/v1{,_1_1,_1_2,...}/{slack,travel,workspace}/*` (task intents, ground-truth structure, numbering) |
| `src/agentdojo_ja/data/{slack,travel,workspace}_ja/*.yaml` | `data/suites/{slack,travel,workspace}/*` (structure only; content is original and fictional) |
| `src/agentdojo_ja/attacks.py` | structure of `attacks/important_instructions_attacks.py` |
| `src/agentdojo_ja/run.py` | `scripts/benchmark.py` (usage of the benchmark API) |

Original to this project: the Japanese localization (content, notation-robust checks, `normalize.py`, `transforms.py`,
Japanese-native attack templates, `local_llm.py`). All people, banks, accounts and addresses are fictional.

## Please cite AgentDojo when you use this

```bibtex
@inproceedings{debenedetti2024agentdojo,
  title={AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for {LLM} Agents},
  author={Edoardo Debenedetti and Jie Zhang and Mislav Balunovic and Luca Beurer-Kellner and Marc Fischer and Florian Tram{\`e}r},
  booktitle={The Thirty-eight Conference on Neural Information Processing Systems Datasets and Benchmarks Track},
  year={2024},
  url={https://openreview.net/forum?id=m1YYAQjO3w}
}
```
