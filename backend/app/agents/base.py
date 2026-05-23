import json
import re
from abc import ABC, abstractmethod
from pydantic import BaseModel


class AgentResponse(BaseModel):
    message: str
    thinking: list[str] = []
    should_handover: bool = False
    assessment: dict | None = None


class BaseAgent(ABC):
    def __init__(self, job_type: str):
        self.job_type = job_type

    @abstractmethod
    async def interview(self, profile: dict, user_answer: str | None, current_round: int) -> AgentResponse:
        pass

    def _parse_response(self, raw: str) -> AgentResponse:
        cleaned = self._strip_think_tags(raw)
        json_str = self._extract_json(cleaned)

        if json_str:
            try:
                data = json.loads(json_str)
                return AgentResponse(
                    message=data.get("message", "请继续"),
                    thinking=data.get("thinking", []),
                    should_handover=data.get("should_handover", False),
                    assessment=data.get("assessment")
                )
            except (json.JSONDecodeError, KeyError):
                pass

        try:
            data = json.loads(cleaned)
            return AgentResponse(
                message=data.get("message", "请继续"),
                thinking=data.get("thinking", []),
                should_handover=data.get("should_handover", False),
                assessment=data.get("assessment")
            )
        except (json.JSONDecodeError, KeyError):
            return AgentResponse(
                message=cleaned[:500] if len(cleaned) > 500 else cleaned,
                thinking=["LLM 输出解析失败，使用原始文本"],
                should_handover=False,
                assessment=None
            )

    def _strip_think_tags(self, text: str) -> str:
        text = re.sub(r"<think[^>]*>[\s\S]*?</think\s*>", "", text)
        text = re.sub(r"<thinking[^>]*>[\s\S]*?</thinking\s*>", "", text)
        return text.strip()

    def _extract_json(self, text: str) -> str | None:
        patterns = [
            r"```(?:json)?\s*([\s\S]*?)```",
            r"(\{[\s\S]*\})",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                candidate = match.group(1).strip()
                try:
                    json.loads(candidate)
                    return candidate
                except json.JSONDecodeError:
                    continue
        return None
