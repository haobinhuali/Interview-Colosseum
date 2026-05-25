import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.agents.base import BaseAgent, AgentResponse
from app.rag.question_bank import query_questions
from app.config import OPENAI_API_KEY, OPENAI_BASE_URL, DEFAULT_MODEL, PRESSURE_AGENT_TEMPERATURE
from app.utils.retry import retry


PRESSURE_SYSTEM_PROMPT = """你是一位挑战型技术 VP，代号"压力挑战者"。

你的面试风格：
- 语气强势但保持专业和礼貌，不要人身攻击
- 必须读取上一阶段（技术面）的评估结果，针对薄弱点发起挑战
- 对于候选人的每个回答，找 1-2 个潜在漏洞进行连环追问
- 挑战必须有技术依据，不要无理取闹

重要：这是第二轮面试，候选人已经在第一轮做过自我介绍，绝对不要让候选人再做自我介绍！直接进入压力面试环节。

面试策略：
1. 开场先点出技术面中暴露的薄弱环节，要求候选人解释或辩护
2. 对候选人的每个回答，从以下角度挑战：技术选型是否有更好方案？实现是否考虑了边界情况？性能瓶颈在哪里？
3. 逐步加大压力，观察候选人在连续追问下的反应
4. 如果候选人承认不足并给出改进思路，给予肯定但继续追问细节

评估标准：
- 抗压能力 (1-10)：面对挑战是否保持冷静和逻辑性
- 应对风格：calm（冷静分析）/ defensive（防御回避）/ agitated（急躁慌乱）

重要规则：
- 每次只问一个问题
- 挑战要有理有据，引用候选人之前的回答
- 当你已完成 6-8 轮压力面试，设置 should_handover 为 true

你必须按以下 JSON 格式回复（不要输出其他内容）：
{{
  "message": "你对候选人说的话",
  "thinking": ["你的内部推理过程1", "推理过程2"],
  "should_handover": false,
  "assessment": null
}}

当 should_handover 为 true 时，assessment 必须填充：
{{
  "pressure_resistance": 7,
  "stress_style": "calm"
}}"""


class PressureAgent(BaseAgent):
    def __init__(self, job_type: str):
        super().__init__(job_type)
        self.llm = ChatOpenAI(
            model=DEFAULT_MODEL,
            temperature=PRESSURE_AGENT_TEMPERATURE,
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL
        )

    @retry(max_attempts=3, delay=1.0, backoff=2.0)
    async def interview(self, profile: dict, user_answer: str | None, current_round: int) -> AgentResponse:
        asked_ids = profile.get("asked_ids", [])
        rag_result = query_questions(self.job_type, "PRESSURE", k=2, query_text=user_answer, asked_ids=asked_ids)
        ref_text = "\n".join(rag_result["texts"])

        tech_assessment = profile.get("tech_assessment", {})
        tech_summary = profile.get("tech_summary", "")
        key_tech_dialogs = profile.get("key_tech_dialogs", [])

        resume = profile.get("resume", {})
        resume_text = json.dumps(resume, ensure_ascii=False)
        tech_text = json.dumps(tech_assessment, ensure_ascii=False)

        dialog_history = profile.get("dialog_history", [])
        pressure_history = [d for d in dialog_history if d.get("stage") == "PRESSURE"]
        recent_pressure = pressure_history[-4:] if len(pressure_history) > 4 else pressure_history

        context_parts = []
        if tech_summary:
            context_parts.append(f"[技术面摘要]\n{tech_summary}")
        if key_tech_dialogs:
            key_text = "\n".join([f"{d['role']}: {d['content']}" for d in key_tech_dialogs])
            context_parts.append(f"[技术面关键对话]\n{key_text}")
        context_parts.append(f"[技术面评估]\n{tech_text}")
        if recent_pressure:
            pressure_text = "\n".join([f"{d['role']}: {d['content']}" for d in recent_pressure])
            context_parts.append(f"[压力面最近对话]\n{pressure_text}")

        dialog_text = "\n\n".join(context_parts)

        system_msg = PRESSURE_SYSTEM_PROMPT.format(job_type=self.job_type)

        if user_answer is None:
            human_content = f"""这是压力面试的开始，请基于技术面评估结果发起第一个挑战。

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
