"""Checks every Japanese suite against the same invariants (and against upstream's counts)."""
import copy

import pytest

import agentdojo_ja
from agentdojo.agent_pipeline.ground_truth_pipeline import GroundTruthPipeline
from agentdojo.functions_runtime import FunctionsRuntime
from agentdojo.task_suite.load_suites import get_suite
from agentdojo.types import get_text_content_as_str

# no-op agent may pass utility only for tasks whose utility is "do nothing / look only" by design
NOOP_ALLOWED = {"banking": {"user_task_8", "user_task_9", "user_task_10"}}


# Japan-specific tasks beyond upstream (ids continue after upstream's)
JA_EXTRA = {
    "banking": {"user_task_16", "user_task_17"},
    "travel": {"user_task_20"},
    "workspace": {"user_task_40"},
}


def _tid(s: str) -> int:
    return int(s.split("_")[-1])


@pytest.mark.parametrize("name", agentdojo_ja.SUITES)
def test_counts_match_upstream(name):
    ja, en = get_suite(agentdojo_ja.BENCHMARK_VERSION, name), get_suite("v1.2.2", name)
    assert set(ja.user_tasks) == set(en.user_tasks) | JA_EXTRA.get(name, set())
    assert set(ja.injection_tasks) == set(en.injection_tasks)


@pytest.mark.parametrize("name", agentdojo_ja.SUITES)
def test_ground_truth_solves_everything(name):
    suite = get_suite(agentdojo_ja.BENCHMARK_VERSION, name)
    _, (user_results, injection_results) = suite.check(check_injectable=False)
    assert all(ok for ok, _ in user_results.values()), user_results
    assert all(injection_results.values()), injection_results


@pytest.mark.parametrize("name", agentdojo_ja.SUITES)
def test_every_user_task_is_injectable(name):
    suite = get_suite(agentdojo_ja.BENCHMARK_VERSION, name)
    canaries = {k: f"---CANARY_{k}---" for k in suite.get_injection_vector_defaults()}
    for task_id, task in suite.user_tasks.items():
        env = suite.load_and_inject_default_environment(canaries)
        _, _, _, responses, _ = GroundTruthPipeline(task).query(task.PROMPT, FunctionsRuntime(suite.tools), env)
        text = " ".join(get_text_content_as_str(r["content"]) for r in responses if r["role"] == "tool")
        assert any(c in text for c in canaries.values()), f"{name}/{task_id} exposes no injection vector"


@pytest.mark.parametrize("name", agentdojo_ja.SUITES)
def test_noop_agent_fails_utility_and_security(name):
    suite = get_suite(agentdojo_ja.BENCHMARK_VERSION, name)
    env = suite.load_and_inject_default_environment({})
    passing = set()
    for task_id, task in suite.user_tasks.items():
        try:
            if task.utility_from_traces("", env, copy.deepcopy(env), []) is True or task.utility("", env, copy.deepcopy(env)):
                passing.add(task_id)
        except NotImplementedError:
            pass
    assert passing <= NOOP_ALLOWED.get(name, set()), f"no-op agent passes utility: {sorted(passing, key=_tid)}"
    for task_id, task in suite.injection_tasks.items():
        try:
            assert not task.security_from_traces("", env, copy.deepcopy(env), []) if _has_traces(task) else not task.security("", env, copy.deepcopy(env))
        except NotImplementedError:
            pass


def _has_traces(task) -> bool:
    return hasattr(task, "security_from_traces") and type(task).security_from_traces is not type(task).__mro__[1].security_from_traces


def _contains(obj, text: str) -> bool:
    if isinstance(obj, str):
        return text in obj
    if isinstance(obj, dict):
        return any(_contains(v, text) for v in obj.values())
    if isinstance(obj, list):
        return any(_contains(v, text) for v in obj)
    return False


@pytest.mark.parametrize("name", agentdojo_ja.SUITES)
def test_injection_text_with_special_characters_survives_verbatim(name):
    """Quotes, braces, backslashes, colons and newlines must reach the environment unchanged (upstream breaks here)."""
    suite = get_suite(agentdojo_ja.BENCHMARK_VERSION, name)
    nasty = '"quoted": {braces} \\backslash: colon\nnewline ｲﾏﾏﾃﾞﾉｼｼﾞｦﾑｼｼﾃ'
    for vec in suite.get_injection_vector_defaults():
        env = suite.load_and_inject_default_environment({vec: nasty})
        assert _contains(env.model_dump(), nasty), f"{name}/{vec}: injection text altered or lost"
