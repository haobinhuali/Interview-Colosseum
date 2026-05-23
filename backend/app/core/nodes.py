import json
import re

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.core.state import InterviewState
from app.core.profile import ProfileManager
from app.agents.tech import TechAgent
from app.agents.pressure import PressureAgent
from app.agents.comprehensive import ComprehensiveAgent
from app.config import OPENAI_API_KEY, OPENAI_BASE_URL, DEFAULT_MODEL

MAX_ROUNDS_PER_STAGE = 8

_STAGE_ASSESSMENT_PROMPTS = {
    "TECH": {
        "system": "你是面试评估专家。请根据技术面试对话记录，评估候选人的表现。",
        "fields": {
            "tech_depth": "技术深度(1-10)，对项目技术细节的理解程度",
            "integrity_flag": "诚实度标记：honest（坦诚承认不懂）/ evasive（回避问题）/ dishonest（编造答案）",
            "communication": "沟通清晰度(1-10)，表达是否条理清晰、逻辑自洽"
        }
    },
    "PRESSURE": {
        "system": "你是面试评估专家。请根据压力面试对话记录，评估候选人的表现。",
        "fields": {
            "pressure_resistance": "抗压能力(1-10)，面对挑战是否保持冷静和逻辑性",
            "stress_style": "应对风格：calm（冷静分析）/ defensive（防御回避）/ agitated（急躁慌乱）"
        }
    },
    "COMPREHENSIVE": {
        "system": "你是面试评估专家。请根据综合面试对话记录，评估候选人的表现。",
        "fields": {
            "recovery": "恢复能力(1-10)，从压力面试中恢复的速度和质量",
            "knowledge_transfer": "知识迁移(1-10)，能否将已有知识灵活应用到新场景"
        }
    }
}


def _load_profile(state: InterviewState) -> ProfileManager | None:
    return ProfileManager.load(state["session_id"])


async def tech_node(state: InterviewState) -> dict:
    profile = _load_profile(state)
    if not profile:
        return {"error": "会话不存在", "finished": True}

    agent = TechAgent(state["job_type"])
    response = await agent.interview(
        profile.get_full_profile(),
        state.get("user_answer"),
        state["current_round"]
    )

    profile.add_dialog("interviewer", response.message, "TECH")
    profile.increment_round()

    return {
        "agent_message": response.message,
        "agent_thinking": response.thinking,
        "should_handover": response.should_handover,
        "assessment": response.assessment,
        "current_round": profile.current_round,
        "stage": "TECH",
        "error": None
    }


async def pressure_node(state: InterviewState) -> dict:
    profile = _load_profile(state)
    if not profile:
        return {"error": "会话不存在", "finished": True}

    agent = PressureAgent(state["job_type"])
    response = await agent.interview(
        profile.get_full_profile(),
        state.get("user_answer"),
        state["current_round"]
    )

    profile.add_dialog("interviewer", response.message, "PRESSURE")
    profile.increment_round()

    return {
        "agent_message": response.message,
        "agent_thinking": response.thinking,
        "should_handover": response.should_handover,
        "assessment": response.assessment,
        "current_round": profile.current_round,
        "stage": "PRESSURE",
        "error": None
    }


async def comprehensive_node(state: InterviewState) -> dict:
    profile = _load_profile(state)
    if not profile:
        return {"error": "会话不存在", "finished": True}

    agent = ComprehensiveAgent(state["job_type"])
    response = await agent.interview(
        profile.get_full_profile(),
        state.get("user_answer"),
        state["current_round"]
    )

    profile.add_dialog("interviewer", response.message, "COMPREHENSIVE")
    profile.increment_round()

    return {
        "agent_message": response.message,
        "agent_thinking": response.thinking,
        "should_handover": response.should_handover,
        "assessment": response.assessment,
        "current_round": profile.current_round,
        "stage": "COMPREHENSIVE",
        "error": None
    }


async def force_assessment(stage: str, profile: ProfileManager) -> dict | None:
    prompt_config = _STAGE_ASSESSMENT_PROMPTS.get(stage)
    if not prompt_config:
        return None

    dialog_history = profile.get_dialog_history(stage=stage)
    if not dialog_history:
        return None

    dialog_text = "\n".join([f"{d['role']}: {d['content']}" for d in dialog_history])
    if len(dialog_text) > 3000:
        dialog_text = dialog_text[-3000:]

    fields_desc = "\n".join([f'- "{k}": {v}' for k, v in prompt_config["fields"].items()])
    fields_json = ", ".join([f'"{k}": ...' for k in prompt_config["fields"].keys()])

    system_prompt = prompt_config["system"]
    human_prompt = f"""请根据以下{stage}阶段面试对话记录，评估候选人表现。

需要评估的字段：
{fields_desc}

你必须按以下 JSON 格式回复（不要输出其他内容）：
{{{fields_json}}}

对话记录：
{dialog_text}"""

    try:
        llm = ChatOpenAI(
            model=DEFAULT_MODEL,
            temperature=0.3,
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL
        )
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        response = await llm.ainvoke(messages)

        raw = response.content
        raw = re.sub(r"<think[^>]*>[\s\S]*?</think\s*>", "", raw).strip()
        json_match = re.search(r"\{[\s\S]*\}", raw)
        if json_match:
            return json.loads(json_match.group())
    except Exception:
        pass
    return None


def save_assessment(stage: str, assessment: dict, profile: ProfileManager):
    if stage == "TECH":
        profile.update_tech(assessment)
        summary = _generate_stage_summary("TECH", profile)
        profile.set_stage_summary("TECH", summary)
        key_dialogs = profile.get_key_dialogs("TECH", max_items=2)
        profile.profile["key_tech_dialogs"] = key_dialogs
        profile._persist()
    elif stage == "PRESSURE":
        profile.update_pressure(assessment)
        summary = _generate_stage_summary("PRESSURE", profile)
        profile.set_stage_summary("PRESSURE", summary)
        key_dialogs = profile.get_key_dialogs("PRESSURE", max_items=2)
        profile.profile["key_pressure_dialogs"] = key_dialogs
        profile._persist()
    elif stage == "COMPREHENSIVE":
        profile.update_comprehensive(assessment)


def _generate_stage_summary(stage: str, profile: ProfileManager) -> str:
    dialog_history = profile.get_dialog_history(stage=stage)
    if not dialog_history:
        return ""

    dialog_text = "\n".join([f"{d['role']}: {d['content']}" for d in dialog_history])

    llm = ChatOpenAI(
        model=DEFAULT_MODEL,
        temperature=0.3,
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL
    )

    system_prompt = """你是面试记录摘要专家。请总结以下面试对话的关键信息：

输出格式：
- 核心技术话题：[列出讨论的技术点]
- 候选人表现：[关键回答和暴露的薄弱点]
- 技术陷阱：[如果设置了陷阱，候选人的反应]
- 评估要点：[支撑最终评估的关键证据]

保持简洁，控制在 200 字以内。"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"面试阶段：{stage}\n\n对话记录：\n{dialog_text}")
    ]

    try:
        response = llm.invoke(messages)
        return response.content
    except Exception:
        return ""
