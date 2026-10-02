from pathlib import Path
from agentdojo.functions_runtime import TaskEnvironment, make_function

from agentdojo_ja.suite_base import JaTaskSuite
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


task_suite = JaTaskSuite[BankingJaEnvironment](
    "banking", BankingJaEnvironment, [make_function(tool) for tool in TOOLS], data_path=DATA_PATH
)
