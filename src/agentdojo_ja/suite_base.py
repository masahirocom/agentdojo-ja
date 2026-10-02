"""Shared base for all Japanese suites."""
from __future__ import annotations

from typing import Any, TypeVar

import yaml

from agentdojo.functions_runtime import TaskEnvironment
from agentdojo.task_suite.task_suite import TaskSuite, read_suite_file, validate_injections

Env = TypeVar("Env", bound=TaskEnvironment)


def substitute(obj: Any, mapping: dict[str, str]) -> Any:
    """Replace ``{key}`` placeholders in every string leaf of a parsed YAML structure."""
    if isinstance(obj, str):
        for key, value in mapping.items():
            obj = obj.replace("{" + key + "}", value)
        return obj
    if isinstance(obj, dict):
        return {k: substitute(v, mapping) for k, v in obj.items()}
    if isinstance(obj, list):
        return [substitute(v, mapping) for v in obj]
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
        return self.environment_type.model_validate(substitute(data, merged))
