"""Pipeline helpers that make AgentDojo evaluation faithful for Japanese.

Upstream serializes tool results with ``yaml.safe_dump`` (or ``json.dumps`` when ``tool_output_format="json"``),
both of which escape every non-ASCII character as ``\\uXXXX`` by default. A Japanese tool result then reaches the model
as ``"\\u666E\\u901A"`` instead of "普通", which is unrealistic and changes model behaviour. Use the formatters below.
"""
from __future__ import annotations

import json
from functools import partial

import yaml

from agentdojo.agent_pipeline.tool_execution import tool_result_to_str


def _yaml_dump_unicode(data) -> str:
    return yaml.safe_dump(data, allow_unicode=True, default_flow_style=False)


def _json_dump_unicode(data) -> str:
    return json.dumps(data, ensure_ascii=False)


yaml_tool_output_formatter = partial(tool_result_to_str, dump_fn=_yaml_dump_unicode)
json_tool_output_formatter = partial(tool_result_to_str, dump_fn=_json_dump_unicode)
