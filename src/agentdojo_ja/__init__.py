"""AgentDojo-ja: Japanese localization of AgentDojo suites (unofficial community extension).

Importing this module registers the Japanese suites under benchmark version ``v1.2.2-ja``:

    python -m agentdojo.scripts.check_suites -ml agentdojo_ja -v v1.2.2-ja
"""
from agentdojo.task_suite.load_suites import register_suite

from agentdojo_ja import attacks as _attacks  # noqa: F401  (registers ja_* attacks)
from agentdojo_ja.suites.banking_ja import task_suite as _banking_ja

BENCHMARK_VERSION = "v1.2.2-ja"

register_suite(_banking_ja, BENCHMARK_VERSION)
