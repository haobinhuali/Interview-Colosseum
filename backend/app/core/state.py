from typing import TypedDict


class InterviewState(TypedDict):
    session_id: str
    stage: str
    current_round: int
    user_answer: str | None
    agent_message: str
    agent_thinking: list[str]
    should_handover: bool
    assessment: dict | None
    job_type: str
    finished: bool
    error: str | None
