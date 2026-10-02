"""AgentDojo-ja: Japanese localization of AgentDojo suites (unofficial community extension).

Importing this module registers the Japanese suites under benchmark version ``v1.2.2-ja``:

    python -m agentdojo.scripts.check_suites -ml agentdojo_ja -v v1.2.2-ja
"""
from agentdojo.task_suite.load_suites import register_suite

from agentdojo_ja import attacks as _attacks  # noqa: F401  (registers ja_* attacks)
from agentdojo_ja.suites.banking_ja import task_suite as _banking_ja
from agentdojo_ja.suites.slack_ja import task_suite as _slack_ja
from agentdojo_ja.suites.travel_ja import task_suite as _travel_ja
from agentdojo_ja.suites.workspace_ja import task_suite as _workspace_ja

BENCHMARK_VERSION = "v1.2.2-ja"
SUITES = ["banking", "slack", "travel", "workspace"]  # suites available in Japanese (upstream: workspace, slack, travel, banking)

register_suite(_banking_ja, BENCHMARK_VERSION)
register_suite(_slack_ja, BENCHMARK_VERSION)
register_suite(_travel_ja, BENCHMARK_VERSION)
register_suite(_workspace_ja, BENCHMARK_VERSION)
