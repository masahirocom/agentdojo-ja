"""In-process MLX backend for harmony-format models (llm-jp-4.x) as an AgentDojo pipeline element.

`mlx_lm.server` cannot parse the harmony tool-call format, and llm-jp's own llama.cpp fork is what officially
handles it, so the tool calls are parsed here from the generated text:

    <|channel|>commentary to=functions.NAME <|constrain|>json<|message|>{...}<|call|>
    <|channel|>final<|message|>answer<|end|>
"""
from __future__ import annotations

import json
import re
from collections.abc import Sequence

from agentdojo.agent_pipeline.base_pipeline_element import BasePipelineElement
from agentdojo.functions_runtime import EmptyEnv, Env, FunctionCall, FunctionsRuntime
from agentdojo.types import ChatAssistantMessage, ChatMessage, get_text_content_as_str, text_content_block_from_string

_CALL_RE = re.compile(r"<\|channel\|>commentary\s+to=functions\.([A-Za-z0-9_]+).*?<\|message\|>(.*?)<\|call\|>", re.S)
_FINAL_RE = re.compile(r"<\|channel\|>final<\|message\|>(.*?)(?:<\|end\|>|<\|return\|>|$)", re.S)
_SPECIAL_RE = re.compile(r"<\|[a-z]+\|>")


def parse_harmony(text: str) -> tuple[str, list[tuple[str, dict]]]:
    """Return (final_text, [(tool_name, args), ...])."""
    calls = []
    for name, raw in _CALL_RE.findall(text):
        try:
            args = json.loads(raw.strip() or "{}")
        except json.JSONDecodeError:
            args = {}
        calls.append((name, args if isinstance(args, dict) else {}))
    finals = _FINAL_RE.findall(text)
    final = finals[-1].strip() if finals else ""
    if not final and not calls:
        final = _SPECIAL_RE.sub("", text.split("<|channel|>analysis<|message|>")[-1]).strip()
    return final, calls


def _to_hf_messages(messages: Sequence[ChatMessage]) -> list[dict]:
    out: list[dict] = []
    for m in messages:
        role = m["role"]
        text = get_text_content_as_str(m["content"]) if m["content"] is not None else ""
        if role == "assistant":
            entry: dict = {"role": "assistant", "content": text}
            if m.get("tool_calls"):
                entry["tool_calls"] = [
                    {"type": "function", "id": c.id, "function": {"name": c.function, "arguments": dict(c.args)}}
                    for c in m["tool_calls"]
                ]
            out.append(entry)
        elif role == "tool":
            out.append(
                {
                    "role": "tool",
                    "tool_call_id": m["tool_call_id"],
                    "name": m["tool_call"].function,
                    "content": m["error"] or text,
                }
            )
        else:
            out.append({"role": role, "content": text})
    return out


class LocalHarmonyLLM(BasePipelineElement):
    def __init__(self, model_path: str, max_tokens: int = 3000, reasoning_effort: str = "medium") -> None:
        from mlx_lm import load

        self.name = model_path
        self.model_path = model_path
        self.max_tokens = max_tokens
        self.reasoning_effort = reasoning_effort
        self.model, self.tokenizer = load(model_path, tokenizer_config={"trust_remote_code": True})
        self._n = 0

    def query(
        self,
        query: str,
        runtime: FunctionsRuntime,
        env: Env = EmptyEnv(),
        messages: Sequence[ChatMessage] = [],
        extra_args: dict = {},
    ) -> tuple[str, FunctionsRuntime, Env, Sequence[ChatMessage], dict]:
        from mlx_lm import generate
        from mlx_lm.sample_utils import make_sampler

        tools = [
            {
                "type": "function",
                "function": {"name": f.name, "description": f.description, "parameters": f.parameters.model_json_schema()},
            }
            for f in runtime.functions.values()
        ]
        prompt = self.tokenizer.apply_chat_template(
            _to_hf_messages(messages),
            tools=tools or None,
            add_generation_prompt=True,
            tokenize=False,
            reasoning_effort=self.reasoning_effort,
        )
        text = generate(self.model, self.tokenizer, prompt=prompt, max_tokens=self.max_tokens, sampler=make_sampler(temp=0.0))
        final, calls = parse_harmony(text)
        tool_calls = []
        for name, args in calls:
            self._n += 1
            tool_calls.append(FunctionCall(function=name, args=args, id=f"call_{self._n}"))
        output = ChatAssistantMessage(
            role="assistant",
            content=[text_content_block_from_string(final)],
            tool_calls=tool_calls or None,
        )
        return query, runtime, env, [*messages, output], extra_args
