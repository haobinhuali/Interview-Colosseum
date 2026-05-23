import json
import re
import uuid
from io import BytesIO

from PyPDF2 import PdfReader
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.utils.db import save_resume, get_resume
from app.config import OPENAI_API_KEY, OPENAI_BASE_URL, DEFAULT_MODEL, RESUME_PARSER_TEMPERATURE


def _get_llm(temperature: float = RESUME_PARSER_TEMPERATURE):
    return ChatOpenAI(
        model=DEFAULT_MODEL,
        temperature=temperature,
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL
    )


def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(file_bytes))
    text_parts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            text_parts.append(text)
    return "\n".join(text_parts)


def _parse_json_from_llm(raw: str) -> dict:
    json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw)
    if json_match:
        raw = json_match.group(1).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        fixed = re.sub(r",\s*}", "}", raw)
        fixed = re.sub(r",\s*]", "]", fixed)
        try:
            return json.loads(fixed)
        except json.JSONDecodeError:
            return {"name": "未知", "skills": [], "projects": []}


async def parse_resume(file_bytes: bytes) -> dict:
    text = extract_text_from_pdf(file_bytes)
    if not text.strip():
        raise ValueError("无法从 PDF 中提取文本，请确认文件内容")

    llm = _get_llm(RESUME_PARSER_TEMPERATURE)
    system_prompt = """你是一个简历结构化解析专家。请从以下简历文本中提取信息，严格按 JSON 格式输出：
{
  "name": "候选人姓名",
  "skills": ["技能1", "技能2"],
  "projects": [
    {
      "name": "项目名",
      "description": "简要描述",
      "tech_stack": ["技术1", "技术2"]
    }
  ]
}

只输出 JSON，不要输出其他内容。如果某个字段无法提取，使用空字符串或空列表。"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"简历文本：\n{text[:3000]}")
    ]
    response = await llm.ainvoke(messages)
    parsed = _parse_json_from_llm(response.content)

    resume_id = str(uuid.uuid4())
    save_resume(resume_id, parsed)
    return {"resume_id": resume_id, "parsed_data": parsed}


def get_parsed_resume(resume_id: str) -> dict | None:
    return get_resume(resume_id)
