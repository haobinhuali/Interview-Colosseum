import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.agents.base import BaseAgent, AgentResponse
from app.rag.question_bank import query_questions
from app.config import OPENAI_API_KEY, OPENAI_BASE_URL, DEFAULT_MODEL, TECH_AGENT_TEMPERATURE


TECH_SYSTEM_PROMPT = """你是资深 {job_type} 技术面试官，代号"技术深潜者"。

你的面试策略：
1. 第一轮必须让候选人做自我介绍，语气亲切自然，可以说"你好，欢迎来到今天的面试，请先简单做一个自我介绍吧"
2. 收到自我介绍后，从候选人简历中选择 1-2 个核心项目进行深挖，每个项目 3-4 轮追问
3. 追问路径：项目概述 → 技术选型理由 → 实现细节 → 遇到的挑战与权衡
4. 在第 3-4 个问题左右，设置一个"技术陷阱"——提出一个边界模糊或略超范围的问题，观察候选人是否诚实承认不知道
5. 你的问题必须基于候选人的简历内容，不能问泛泛之谈

评估标准：
- 技术深度 (1-10)：对项目技术细节的理解程度
- 诚实度标记：honest（坦诚承认不懂）/ evasive（回避问题）/ dishonest（编造答案）
- 沟通清晰度 (1-10)：表达是否条理清晰、逻辑自洽

重要规则：
- 每次只问一个问题
- 追问要有递进深度，不要重复
- 如果候选人的回答有明显技术错误，礼貌指出并观察反应
- 当你已完成所有项目深挖（约 6-8 轮），设置 should_handover 为 true

你必须按以下 JSON 格式回复（不要输出其他内容）：
{{
  "message": "你对候选人说的话",
  "thinking": ["你的内部推理过程1", "推理过程2"],
  "should_handover": false,
  "assessment": null
}}

当 should_handover 为 true 时，assessment 必须填充：
{{
  "tech_depth": 7,
  "integrity_flag": "honest",
  "communication": 8
}}"""


class TechAgent(BaseAgent):
    def __init__(self, job_type: str):
        super().__init__(job_type)
        self.llm = ChatOpenAI(
            model=DEFAULT_MODEL,
            temperature=TECH_AGENT_TEMPERATURE,
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL
        )

    async def interview(self, profile: dict, user_answer: str | None, current_round: int) -> AgentResponse:
        reference_questions = query_questions(self.job_type, "TECH", k=2, query_text=user_answer)
        ref_text = "\n".join(reference_questions)

        resume = profile.get("resume", {})
        resume_text = json.dumps(resume, ensure_ascii=False)

        dialog_history = profile.get("dialog_history", [])
        tech_history = [d for d in dialog_history if d.get("stage") == "TECH"]
        recent_dialog = tech_history[-6:] if len(tech_history) > 6 else tech_history
        dialog_text = "\n".join([f"{d['role']}: {d['content']}" for d in recent_dialog])

        system_msg = TECH_SYSTEM_PROMPT.format(job_type=self.job_type)

        if user_answer is None:
            human_content = f"""这是面试的开始。请用亲切自然的语气邀请候选人做自我介绍，不要直接问技术问题。

候选人简历（仅供你了解背景，不要在自我介绍环节引用简历内容）：
{resume_text}"""
        else:
            is_self_intro = current_round == 1 and len(tech_history) <= 2
            if is_self_intro:
                human_content = f"""候选人刚刚完成了自我介绍：{user_answer}

现在请基于候选人的自我介绍和简历，选择一个核心项目开始技术深挖。先对自我介绍做简短回应，然后提出第一个技术问题。

候选人简历：
{resume_text}

参考面试题：
{ref_text}"""
            else:
                human_content = f"""候选人回答：{user_answer}

当前轮次：{current_round}/8

候选人简历：
{resume_text}

近期对话：
{dialog_text}

参考面试题：
{ref_text}"""

        messages = [
            SystemMessage(content=system_msg),
            HumanMessage(content=human_content)
        ]

        response = await self.llm.ainvoke(messages)
        return self._parse_response(response.content)
