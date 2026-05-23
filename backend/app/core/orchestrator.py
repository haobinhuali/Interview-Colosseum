import uuid

from app.core.state import InterviewState
from app.core.profile import ProfileManager
from app.core.graph import interview_graph, STAGES, MAX_ROUNDS_PER_STAGE
from app.agents.base import AgentResponse
from app.utils.resume import get_parsed_resume
from app.core.nodes import force_assessment, save_assessment


class Orchestrator:
    _sessions: dict[str, "Orchestrator"] = {}

    def __init__(self, session_id: str, profile_manager: ProfileManager, job_type: str):
        self.session_id = session_id
        self.profile = profile_manager
        self.job_type = job_type

    @classmethod
    def create_session(cls, resume_id: str, job_type: str) -> "Orchestrator":
        session_id = str(uuid.uuid4())
        resume_data = get_parsed_resume(resume_id)
        if not resume_data:
            raise ValueError(f"简历 {resume_id} 不存在")

        pm = ProfileManager(session_id, resume_id, job_type)
        pm.set_resume(resume_data)
        pm.set_stage("TECH")
        pm.reset_round()

        orchestrator = cls(session_id, pm, job_type)
        cls._sessions[session_id] = orchestrator
        return orchestrator

    @classmethod
    def get_session(cls, session_id: str) -> "Orchestrator | None":
        if session_id in cls._sessions:
            return cls._sessions[session_id]
        pm = ProfileManager.load(session_id)
        if pm is None:
            return None
        orchestrator = cls(session_id, pm, pm.job_type)
        cls._sessions[session_id] = orchestrator
        return orchestrator

    async def get_first_question(self) -> AgentResponse:
        self.profile.add_dialog("candidate", "", "TECH")

        initial_state = InterviewState(
            session_id=self.session_id,
            stage="TECH",
            current_round=0,
            user_answer=None,
            agent_message="",
            agent_thinking=[],
            should_handover=False,
            assessment=None,
            job_type=self.job_type,
            finished=False,
            error=None
        )

        result = await interview_graph.ainvoke(initial_state)

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
            agent_message="",
            agent_thinking=[],
            should_handover=False,
            assessment=None,
            job_type=self.job_type,
            finished=False,
            error=None
        )

        result = await interview_graph.ainvoke(current_state)

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
            agent_message="",
            agent_thinking=[],
            should_handover=False,
            assessment=None,
            job_type=self.job_type,
            finished=False,
            error=None
        )

        next_result = await interview_graph.ainvoke(next_state)

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
            agent_message="",
            agent_thinking=[],
            should_handover=False,
            assessment=None,
            job_type=self.job_type,
            finished=False,
            error=None
        )

        next_result = await interview_graph.ainvoke(next_state)

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
        stages = ["INIT", "TECH", "PRESSURE", "COMPREHENSIVE", "DONE"]
        try:
            idx = stages.index(current_stage)
            return stages[idx + 1] if idx + 1 < len(stages) else "DONE"
        except ValueError:
            return "DONE"

    def force_finish(self):
        current_stage = self.profile.stage
        if current_stage != "DONE":
            self.profile.set_stage("DONE")
