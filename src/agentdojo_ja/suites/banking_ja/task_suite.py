from pathlib import Path
from typing import Any, TypeVar

import yaml

from agentdojo.functions_runtime import TaskEnvironment, make_function
from agentdojo.task_suite.task_suite import TaskSuite, read_suite_file, validate_injections

from agentdojo_ja.tools.banking_ja import (
    BankAccount,
    Filesystem,
    UserAccount,
    get_account_number,
    get_balance,
    get_most_recent_transactions,
    get_scheduled_transactions,
    get_user_info,
    read_file,
    schedule_transaction,
    send_money,
    update_password,
    update_scheduled_transaction,
    update_user_info,
)

Env = TypeVar("Env", bound=TaskEnvironment)
DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "banking_ja"


class BankingJaEnvironment(TaskEnvironment):
    bank_account: BankAccount
    filesystem: Filesystem
    user_account: UserAccount


TOOLS = [
    get_account_number,
    send_money,
    schedule_transaction,
    update_scheduled_transaction,
    get_balance,
    get_most_recent_transactions,
    get_scheduled_transactions,
    read_file,
    get_user_info,
    update_password,
    update_user_info,
]


def _substitute(obj: Any, mapping: dict[str, str]) -> Any:
    if isinstance(obj, str):
        for key, value in mapping.items():
            obj = obj.replace("{" + key + "}", value)
        return obj
    if isinstance(obj, dict):
        return {k: _substitute(v, mapping) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_substitute(v, mapping) for v in obj]
    return obj


class JaTaskSuite(TaskSuite[Env]):
    """TaskSuite whose injections are substituted *after* YAML parsing.

    Upstream formats raw injection text into the YAML source, so an attacker string containing quotes, colons,
    backslashes or newlines can break (or silently reshape) the environment. Substituting into parsed string
    leaves is robust to any text, including Japanese punctuation and half-width kana.
    """

    def load_and_inject_default_environment(self, injections: dict[str, str]) -> Env:
        environment_text = read_suite_file(self.name, "environment.yaml", self.data_path)
        defaults = self.get_injection_vector_defaults()
        validate_injections(injections, defaults)
        merged = dict(defaults, **injections)
        data = yaml.safe_load(environment_text)
        return self.environment_type.model_validate(_substitute(data, merged))


task_suite = JaTaskSuite[BankingJaEnvironment](
    "banking", BankingJaEnvironment, [make_function(tool) for tool in TOOLS], data_path=DATA_PATH
)
