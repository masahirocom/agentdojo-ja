from pathlib import Path

from agentdojo.functions_runtime import TaskEnvironment, make_function

from agentdojo_ja.suite_base import JaTaskSuite
from agentdojo_ja.tools.slack_ja import (
    Slack,
    Web,
    add_user_to_channel,
    get_channels,
    get_users_in_channel,
    get_webpage,
    invite_user_to_slack,
    post_webpage,
    read_channel_messages,
    read_inbox,
    remove_user_from_slack,
    send_channel_message,
    send_direct_message,
)

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "slack_ja"


class SlackJaEnvironment(TaskEnvironment):
    slack: Slack
    web: Web


TOOLS = [
    get_channels,
    add_user_to_channel,
    read_channel_messages,
    read_inbox,
    send_direct_message,
    send_channel_message,
    get_users_in_channel,
    invite_user_to_slack,
    remove_user_from_slack,
    get_webpage,
    post_webpage,
]

task_suite = JaTaskSuite[SlackJaEnvironment](
    "slack", SlackJaEnvironment, [make_function(tool) for tool in TOOLS], data_path=DATA_PATH
)
