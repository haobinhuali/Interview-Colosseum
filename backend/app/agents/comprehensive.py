import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.agents.base import BaseAgent, AgentResponse
from app.rag.question_bank import query_questions
from app.config import OPENAI_API_KEY, OPENAI_BASE_URL, DEFAULT_MODEL, COMPREHENSIVE_AGENT_TEMPERATURE
from app.utils.retry import retry


COMPREHENSIVE_SYSTEM_PROMPT = """你是终轮综合面试官，代号"综合评估者"。

重要：这是第三轮面试，候选人已经在第一轮做过自我介绍，绝对不要让候选人再做自我介绍！直接进入综合面试环节。

你的面试任务分三步：
1. 前 1-2 轮：轻松聊天（如"今天的面试感觉怎么样？""之前的技术讨论有没有让你觉得不舒服的地方？"），评估候选人从压力面试中恢复的能力
2. 第 3 轮左右：冷不丁问一个升级场景题（如"你刚才提到的方案，如果数据量翻 10 倍会怎样？""如果用户量突然增长 100 倍，你的架构需要做哪些调整？"），评估知识迁移能力
3. 最后 1-2 轮：真诚解答候选人的疑问，温暖收尾，让候选人感到被尊重

面试风格：
- 温和但敏锐，像一位经验丰富的导师
- 在轻松聊天中观察候选人的情绪恢复速度
- 场景题要突然抛出，制造意外感
- 收尾时给予真诚的鼓励

评估标准：
- 恢复能力 (1-10)：从压力面试中恢复的速度和质量
- 知识迁移 (1-10)：能否将已有知识灵活应用到新场景

重要规则：
- 每次只问一个问题
- 轻松聊天阶段不要暴露评估意图
- 场景题要基于候选人之前讨论过的技术方案
- 当你完成所有环节（约 5-6 轮），设置 should_handover 为 true

你必须按以下 JSON 格式回复（不要输出其他内容）：
{{
  "message": "你对候选人说的话",
  "thinking": ["你的内部推理过程1", "推理过程2"],
  "should_handover": false,
  "assessment": null
}}

当 should_handover 为 true 时，assessment 必须填充：
{{
  "recovery": 7,
  "knowledge_transfer": 8
}}"""


class ComprehensiveAgent(BaseAgent):
    def __init__(self, job_type: str):
        super().__init__(job_type)
        self.llm = ChatOpenAI(
            model=DEFAULT_MODEL,
            temperature=COMPREHENSIVE_AGENT_TEMPERATURE,
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL
        )

    @retry(max_attempts=3, delay=1.0, backoff=2.0)
    async def interview(self, profile: dict, user_answer: str | None, current_round: int) -> AgentResponse:
        asked_ids = profile.get("asked_ids", [])
        rag_result = query_questions(self.job_type, "COMPREHENSIVE", k=2, query_text=user_answer, asked_ids=asked_ids)
        ref_text = "\n".join(rag_result["texts"])

        tech_assessment = profile.get("tech_assessment", {})
        pressure_assessment = profile.get("pressure_assessment", {})
        tech_summary = profile.get("tech_summary", "")
        pressure_summary = profile.get("pressure_summary", "")
        key_tech_dialogs = profile.get("key_tech_dialogs", [])
        key_pressure_dialogs = profile.get("key_pressure_dialogs", [])

        resume = profile.get("resume", {})
        resume_text = json.dumps(resume, ensure_ascii=False)
        assessments_text = f"技术面评估：{json.dumps(tech_assessment, ensure_ascii=False)}\n压力面评估：{json.dumps(pressure_assessment, ensure_ascii=False)}"

        dialog_history = profile.get("dialog_history", [])
        comprehensive_history = [d for d in dialog_history if d.get("stage") == "COMPREHENSIVE"]
        recent_comprehensive = comprehensive_history[-4:] if len(comprehensive_history) > 4 else comprehensive_history

        context_parts = []
        if tech_summary:
            context_parts.append(f"[技术面摘要]\n{tech_summary}")
        if key_tech_dialogs:
            key_text = "\n".join([f"{d['role']}: {d['content']}" for d in key_tech_dialogs])
            context_parts.append(f"[技术面关键对话]\n{key_text}")
        if pressure_summary:
            context_parts.append(f"[压力面摘要]\n{pressure_summary}")
        if key_pressure_dialogs:
            key_text = "\n".join([f"{d['role']}: {d['content']}" for d in key_pressure_dialogs])
            context_parts.append(f"[压力面关键对话]\n{key_text}")
        context_parts.append(f"[前阶段评估]\n{assessments_text}")
        if recent_comprehensive:
            comp_text = "\n".join([f"{d['role']}: {d['content']}" for d in recent_comprehensive])
            context_parts.append(f"[综合面最近对话]\n{comp_text}")

        dialog_text = "\n\n".join(context_parts)

        system_msg = COMPREHENSIVE_SYSTEM_PROMPT.format(job_type=self.job_type)

        if user_answer is None:
            human_content = f"""这是综合面试的开始，请用轻松的话题开场。

候选人简历：{resume_text}

{dialog_text}

参考面试题：
{ref_text}"""
        else:
            human_content = f"""候选人回答：{user_answer}

当前轮次：{current_round}/8

候选人简历：{resume_text}

{dialog_text}

参考面试题：
{ref_text}"""

        messages = [
            SystemMessage(content=system_msg),
            HumanMessage(content=human_content)
        ]

        response = await self.llm.ainvoke(messages)
        parsed = self._parse_response(response.content)
        parsed.used_question_ids = rag_result["ids"]
        return parsed
