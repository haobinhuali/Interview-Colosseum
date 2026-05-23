import json
import re
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.core.profile import ProfileManager
from app.config import OPENAI_API_KEY, OPENAI_BASE_URL, DEFAULT_MODEL, EVALUATOR_TEMPERATURE


EVALUATOR_SYSTEM_PROMPT = """你是一位资深面试评估专家。你需要根据三个面试官的评估结果和完整对话记录，生成一份综合评估报告。

评估维度和权重：
- 技术深度 (40%)：基于技术面评估的 tech_depth 和 communication
- 抗压能力 (30%)：基于压力面评估的 pressure_resistance
- 逻辑表达 (15%)：基于技术面的 communication 和综合面的 knowledge_transfer
- 诚信度 (15%)：基于技术面的 integrity_flag 和压力面的 stress_style

你需要：
1. 计算每个维度的 1-10 分数
2. 生成雷达图数据
3. 撰写 3 条具体改进建议，每条必须引用面试中的实际表现
4. 对每个面试问题，给出建议回复（更好的回答方式或补充要点）

你必须按以下 JSON 格式回复（不要输出其他内容）：
{{
  "summary": "一段 100 字左右的综合评价",
  "scores": {{
    "tech_depth": 7,
    "pressure_resistance": 6,
    "communication": 8,
    "integrity": 9
  }},
  "radar_data": [
    {{ "dim": "技术深度", "score": 7 }},
    {{ "dim": "逻辑表达", "score": 8 }},
    {{ "dim": "抗压能力", "score": 6 }},
    {{ "dim": "诚信度", "score": 9 }}
  ],
  "suggestions": [
    {{
      "title": "建议标题",
      "content": "具体建议内容，引用面试中的实际表现",
      "evidence": "面试中的具体对话证据"
    }}
  ],
  "qa_review": [
    {{
      "stage": "TECH",
      "question": "面试官提出的问题",
      "answer": "候选人的回答",
      "suggested_answer": "建议的更好回答，包含关键要点和补充内容"
    }}
  ]
}}"""


async def generate_report(profile_manager: ProfileManager) -> dict:
    profile = profile_manager.get_full_profile()
    tech = profile.get("tech_assessment", {})
    pressure = profile.get("pressure_assessment", {})
    comprehensive = profile.get("comprehensive_assessment", {})
    dialog_history = profile.get("dialog_history", [])

    dialog_text = "\n".join([
        f"[{d['stage']}] {d['role']}: {d['content']}"
        for d in dialog_history
    ])

    qa_pairs = _extract_qa_pairs(dialog_history)

    integrity_score = _integrity_to_score(tech.get("integrity_flag", ""))
    stress_bonus = _stress_style_to_bonus(pressure.get("stress_style", ""))

    preliminary_scores = {
        "tech_depth": min(10, max(1, tech.get("tech_depth", 5))),
        "pressure_resistance": min(10, max(1, pressure.get("pressure_resistance", 5) + stress_bonus)),
        "communication": min(10, max(1, tech.get("communication", 5))),
        "integrity": min(10, max(1, integrity_score))
    }

    weighted_total = (
        preliminary_scores["tech_depth"] * 0.4
        + preliminary_scores["pressure_resistance"] * 0.3
        + preliminary_scores["communication"] * 0.15
        + preliminary_scores["integrity"] * 0.15
    )

    llm = ChatOpenAI(
        model=DEFAULT_MODEL,
        temperature=EVALUATOR_TEMPERATURE,
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL
    )

    qa_text = "\n".join([
        f"[{p['stage']}] Q: {p['question']}\nA: {p['answer']}"
        for p in qa_pairs
    ])

    human_content = f"""请根据以下面试数据生成评估报告：

技术面评估：{json.dumps(tech, ensure_ascii=False)}
压力面评估：{json.dumps(pressure, ensure_ascii=False)}
综合面评估：{json.dumps(comprehensive, ensure_ascii=False)}

初步计算分数（供参考，你可以根据对话内容微调）：
{json.dumps(preliminary_scores, ensure_ascii=False)}

加权总分：{weighted_total:.1f}/10

问答记录（请为每一对问答生成建议回复）：
{qa_text[:6000]}

完整对话记录：
{dialog_text[:4000]}"""

    messages = [
        SystemMessage(content=EVALUATOR_SYSTEM_PROMPT),
        HumanMessage(content=human_content)
    ]

    response = await llm.ainvoke(messages)
    report = _parse_report(response.content)

    report["scores"] = report.get("scores", preliminary_scores)
    report["radar_data"] = report.get("radar_data", [
        {"dim": "技术深度", "score": preliminary_scores["tech_depth"]},
        {"dim": "逻辑表达", "score": preliminary_scores["communication"]},
        {"dim": "抗压能力", "score": preliminary_scores["pressure_resistance"]},
        {"dim": "诚信度", "score": preliminary_scores["integrity"]}
    ])
    report["weighted_total"] = round(weighted_total, 1)
    report["qa_review"] = report.get("qa_review", qa_pairs)
    report["full_dialog"] = _format_full_dialog(dialog_history)

    return report


def _extract_qa_pairs(dialog_history: list) -> list[dict]:
    pairs = []
    i = 0
    while i < len(dialog_history):
        if dialog_history[i]["role"] == "interviewer":
            question = dialog_history[i]["content"]
            stage = dialog_history[i].get("stage", "")
            answer = ""
            if i + 1 < len(dialog_history) and dialog_history[i + 1]["role"] == "candidate":
                answer = dialog_history[i + 1]["content"]
                i += 2
            else:
                i += 1
            pairs.append({
                "stage": stage,
                "question": question,
                "answer": answer,
                "suggested_answer": ""
            })
        else:
            i += 1
    return pairs


def _format_full_dialog(dialog_history: list) -> list[dict]:
    stage_labels = {
        "TECH": "技术面",
        "PRESSURE": "压力面",
        "COMPREHENSIVE": "综合面"
    }
    result = []
    for d in dialog_history:
        role_label = "面试官" if d["role"] == "interviewer" else "候选人"
        result.append({
            "stage": stage_labels.get(d.get("stage", ""), d.get("stage", "")),
            "role": role_label,
            "content": d["content"]
        })
    return result


def _integrity_to_score(flag: str) -> int:
    mapping = {"honest": 9, "evasive": 5, "dishonest": 2}
    return mapping.get(flag, 5)


def _stress_style_to_bonus(style: str) -> int:
    mapping = {"calm": 1, "defensive": 0, "agitated": -1}
    return mapping.get(style, 0)


def _parse_report(raw: str) -> dict:
    try:
        cleaned = re.sub(r"<think[^>]*>[\s\S]*?</think\s*>", "", raw).strip()
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", cleaned)
        if json_match:
            return json.loads(json_match.group(1).strip())
        json_match = re.search(r"\{[\s\S]*\}", cleaned)
        if json_match:
            return json.loads(json_match.group())
    except (json.JSONDecodeError, KeyError):
        pass
    return {
        "summary": "评估报告生成失败，请重新生成",
        "scores": {},
        "radar_data": [],
        "suggestions": [],
        "qa_review": []
    }
