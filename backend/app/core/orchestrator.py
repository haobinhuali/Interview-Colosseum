import uuid
import time
from collections import OrderedDict

from pydantic import BaseModel

from app.core.profile import ProfileManager
from app.agents.base import AgentResponse
from app.utils.resume import get_parsed_resume
from app.utils.db import get_active_session_by_resume
from app.core.nodes import (
    tech_node,
    pressure_node,
    comprehensive_node,
    force_assessment,
    save_assessment,
)

STAGES = ["INIT", "TECH", "PRESSURE", "COMPREHENSIVE", "DONE"]
MAX_ROUNDS_PER_STAGE = 8

_NODE_MAP = {
    "TECH": tech_node,
    "PRESSURE": pressure_node,
    "COMPREHENSIVE": comprehensive_node,
}


class InterviewState(BaseModel):
    session_id: str
    stage: str
    current_round: int
    user_answer: str | None = None
    agent_message: str = ""
    agent_thinking: list[str] = []
    should_handover: bool = False
    assessment: dict | None = None
    job_type: str
    finished: bool = False
    error: str | None = None
    asked_question_ids: list[str] = []


class Orchestrator:
    _sessions: OrderedDict[str, tuple["Orchestrator", float]] = OrderedDict()
    _MAX_CACHE_SIZE = 100
    _TTL_SECONDS = 3600

    def __init__(self, session_id: str, profile_manager: ProfileManager, job_type: str):
        self.session_id = session_id
        self.profile = profile_manager
        self.job_type = job_type

    @classmethod
    def create_session(cls, resume_id: str, job_type: str) -> "Orchestrator":
        active = get_active_session_by_resume(resume_id)
        if active:
            existing = cls.get_session(active["session_id"])
            if existing:
                return existing

        session_id = str(uuid.uuid4())
        resume_data = get_parsed_resume(resume_id)
        if not resume_data:
            raise ValueError(f"简历 {resume_id} 不存在")

        pm = ProfileManager(session_id, resume_id, job_type)
        pm.set_resume(resume_data)
        pm.set_stage("TECH")
        pm.reset_round()

        orchestrator = cls(session_id, pm, job_type)
        cls._put_cache(session_id, orchestrator)
        return orchestrator

    @classmethod
    def get_session(cls, session_id: str) -> "Orchestrator | None":
        if session_id in cls._sessions:
            orchestrator, timestamp = cls._sessions[session_id]
            if time.time() - timestamp < cls._TTL_SECONDS:
                cls._sessions.move_to_end(session_id)
                return orchestrator
            else:
                del cls._sessions[session_id]

        pm = ProfileManager.load(session_id)
        if pm is None:
            return None
        orchestrator = cls(session_id, pm, pm.job_type)
        cls._put_cache(session_id, orchestrator)
        return orchestrator

    @classmethod
    def _put_cache(cls, session_id: str, orchestrator: "Orchestrator"):
        cls._sessions[session_id] = (orchestrator, time.time())
        cls._sessions.move_to_end(session_id)
        cls._evict_cache()

    @classmethod
    def _evict_cache(cls):
        now = time.time()
        while cls._sessions:
            sid, (_, ts) = next(iter(cls._sessions.items()))
            if now - ts >= cls._TTL_SECONDS or len(cls._sessions) > cls._MAX_CACHE_SIZE:
                cls._sessions.popitem(last=False)
            else:
                break

    async def _run_node(self, state: InterviewState) -> dict:
        node_func = _NODE_MAP.get(state.stage)
        if not node_func:
            return {"error": f"未知阶段: {state.stage}", "finished": True}
        return await node_func(state.model_dump())

    async def get_first_question(self) -> AgentResponse:
        self.profile.add_dialog("candidate", "", "TECH")

        initial_state = InterviewState(
            session_id=self.session_id,
            stage="TECH",
            current_round=0,
            user_answer=None,
            job_type=self.job_type,
            asked_question_ids=self.profile.get_asked_ids()
        )

        result = await self._run_node(initial_state)
        self._sync_asked_ids(result)

        return AgentResponse(
            message=result.get("agent_message", "请开始面试"),
            thinking=result.get("agent_thinking", [])
        )

    async def process_turn(self, user_answer: str) -> dict:
        current_stage = self.profile.stage
        if current_stage == "DONE":
            return {
                "message": "面试已结束",
                "thinking": [],
                "stage": "DONE",
                "round": self.profile.current_round,
                "finished": True,
                "should_handover": False
            }

        self.profile.add_dialog("candidate", user_answer, current_stage)

        current_state = InterviewState(
            session_id=self.session_id,
            stage=current_stage,
            current_round=self.profile.current_round,
            user_answer=user_answer,
            job_type=self.job_type,
            asked_question_ids=self.profile.get_asked_ids()
        )

        result = await self._run_node(current_state)
        self._sync_asked_ids(result)

        if result.get("error"):
            return {
                "message": result.get("error", "处理失败"),
                "thinking": [],
                "stage": current_stage,
                "round": self.profile.current_round,
                "finished": False,
                "should_handover": False
            }

        should_handover = result.get("should_handover", False)
        current_round = result.get("current_round", self.profile.current_round)

        if current_round >= MAX_ROUNDS_PER_STAGE:
            should_handover = True

        if should_handover:
            return await self._handle_handover(current_stage, result)

        return {
            "message": result.get("agent_message", "请继续"),
            "thinking": result.get("agent_thinking", []),
            "stage": current_stage,
            "round": current_round,
            "finished": False,
            "should_handover": False
        }

    async def _handle_handover(self, current_stage: str, result: dict) -> dict:
        assessment = result.get("assessment")
        if not assessment:
            assessment = await force_assessment(current_stage, self.profile)
        if assessment:
            save_assessment(current_stage, assessment, self.profile)

        next_stage = self._get_next_stage(current_stage)

        if next_stage == "DONE":
            self.profile.set_stage("DONE")
            return {
                "message": result.get("agent_message", "面试结束"),
                "thinking": result.get("agent_thinking", []),
                "stage": "DONE",
                "round": self.profile.current_round,
                "finished": True,
                "should_handover": True
            }

        self.profile.set_stage(next_stage)
        self.profile.reset_round()

        next_state = InterviewState(
            session_id=self.session_id,
            stage=next_stage,
            current_round=0,
            user_answer=None,
            job_type=self.job_type,
            asked_question_ids=self.profile.get_asked_ids()
        )

        next_result = await self._run_node(next_state)
        self._sync_asked_ids(next_result)

        return {
            "message": next_result.get("agent_message", "请继续"),
            "thinking": next_result.get("agent_thinking", []),
            "stage": next_stage,
            "round": self.profile.current_round,
            "finished": False,
            "should_handover": True
        }

    async def skip_stage(self) -> dict:
        current_stage = self.profile.stage
        if current_stage == "DONE":
            return {
                "message": "面试已结束",
                "thinking": [],
                "stage": "DONE",
                "round": self.profile.current_round,
                "finished": True,
                "should_handover": False
            }

        assessment = await force_assessment(current_stage, self.profile)
        if assessment:
            save_assessment(current_stage, assessment, self.profile)

        next_stage = self._get_next_stage(current_stage)

        if next_stage == "DONE":
            self.profile.set_stage("DONE")
            return {
                "message": "已跳过当前阶段，面试结束",
                "thinking": [],
                "stage": "DONE",
                "round": self.profile.current_round,
                "finished": True,
                "should_handover": True
            }

        self.profile.set_stage(next_stage)
        self.profile.reset_round()

        next_state = InterviewState(
            session_id=self.session_id,
            stage=next_stage,
            current_round=0,
            user_answer=None,
            job_type=self.job_type,
            asked_question_ids=self.profile.get_asked_ids()
        )

        next_result = await self._run_node(next_state)
        self._sync_asked_ids(next_result)

        return {
            "message": next_result.get("agent_message", "请继续"),
            "thinking": next_result.get("agent_thinking", []),
            "stage": next_stage,
            "round": self.profile.current_round,
            "finished": False,
            "should_handover": True
        }

    async def jump_to_final(self) -> dict:
        current_stage = self.profile.stage
        if current_stage == "DONE":
            return {
                "message": "面试已结束",
                "thinking": [],
                "stage": "DONE",
                "round": self.profile.current_round,
                "finished": True,
                "should_handover": False
            }

        stage_idx = STAGES.index(current_stage) if current_stage in STAGES else len(STAGES)
        for stage in STAGES:
            if STAGES.index(stage) >= stage_idx and stage not in ("INIT", "DONE"):
                dialog_history = self.profile.get_dialog_history(stage=stage)
                if dialog_history:
                    assessment = await force_assessment(stage, self.profile)
                    if assessment:
                        save_assessment(stage, assessment, self.profile)

        self.profile.set_stage("DONE")
        return {
            "message": "已跳过所有剩余阶段，直接进入最终评估",
            "thinking": [],
            "stage": "DONE",
            "round": self.profile.current_round,
            "finished": True,
            "should_handover": True
        }

    def _get_next_stage(self, current_stage: str) -> str:
        try:
            idx = STAGES.index(current_stage)
            return STAGES[idx + 1] if idx + 1 < len(STAGES) else "DONE"
        except ValueError:
            return "DONE"

    def _sync_asked_ids(self, result: dict):
        asked_from_state = result.get("asked_question_ids", [])
        if asked_from_state:
            current = set(self.profile.profile.get("asked_ids", []))
            current.update(asked_from_state)
            self.profile.profile["asked_ids"] = list(current)
            self.profile._persist()

    def force_finish(self):
        current_stage = self.profile.stage
        if current_stage != "DONE":
            self.profile.set_stage("DONE")
