from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

from app.utils.resume import parse_resume
from app.core.orchestrator import Orchestrator
from app.core.evaluator import generate_report
from app.rag.question_bank import add_custom_questions, get_question_bank_stats

router = APIRouter()


class StartInterviewRequest(BaseModel):
    resume_id: str
    job_type: str = "AI Agent 开发工程师"


class InterviewNextRequest(BaseModel):
    session_id: str
    user_answer: str


class SessionIdRequest(BaseModel):
    session_id: str


class GenerateReportRequest(BaseModel):
    session_id: str


@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="仅支持 PDF 文件")

    try:
        file_bytes = await file.read()
        result = await parse_resume(file_bytes)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"简历解析失败: {str(e)}")


@router.post("/start-interview")
async def start_interview(request: StartInterviewRequest):
    try:
        orchestrator = Orchestrator.create_session(request.resume_id, request.job_type)
        first_response = await orchestrator.get_first_question()
        return {
            "session_id": orchestrator.session_id,
            "stage": "TECH",
            "first_message": first_response.message,
            "thinking": first_response.thinking
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动面试失败: {str(e)}")


@router.post("/interview-next")
async def interview_next(request: InterviewNextRequest):
    orchestrator = Orchestrator.get_session(request.session_id)
    if not orchestrator:
        raise HTTPException(status_code=404, detail="面试会话不存在")

    try:
        result = await orchestrator.process_turn(request.user_answer)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"对话处理失败: {str(e)}")


@router.post("/skip-stage")
async def skip_stage(request: SessionIdRequest):
    orchestrator = Orchestrator.get_session(request.session_id)
    if not orchestrator:
        raise HTTPException(status_code=404, detail="面试会话不存在")

    try:
        result = await orchestrator.skip_stage()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"跳过阶段失败: {str(e)}")


@router.post("/jump-to-final")
async def jump_to_final(request: SessionIdRequest):
    orchestrator = Orchestrator.get_session(request.session_id)
    if not orchestrator:
        raise HTTPException(status_code=404, detail="面试会话不存在")

    try:
        result = await orchestrator.jump_to_final()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"跳转到最终评估失败: {str(e)}")


@router.post("/generate-report")
async def generate_report_endpoint(request: GenerateReportRequest):
    orchestrator = Orchestrator.get_session(request.session_id)
    if not orchestrator:
        raise HTTPException(status_code=404, detail="面试会话不存在")

    try:
        report = await generate_report(orchestrator.profile)
        return {"report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"报告生成失败: {str(e)}")


@router.post("/upload-questions")
async def upload_questions(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")

    if not (file.filename.lower().endswith(".json") or file.filename.lower().endswith(".jsonl")):
        raise HTTPException(status_code=400, detail="仅支持 JSON 文件")

    try:
        content = await file.read()
        text = content.decode("utf-8")
        import json

        if file.filename.lower().endswith(".jsonl"):
            questions = [json.loads(line) for line in text.strip().split("\n") if line.strip()]
        else:
            data = json.loads(text)
            questions = data if isinstance(data, list) else [data]

        required_fields = {"question", "stage"}
        for i, q in enumerate(questions):
            if not isinstance(q, dict):
                raise HTTPException(status_code=400, detail=f"第 {i + 1} 条数据格式错误，必须是 JSON 对象")
            missing = required_fields - set(q.keys())
            if missing:
                raise HTTPException(status_code=400, detail=f"第 {i + 1} 条数据缺少必填字段: {missing}")

        count = add_custom_questions(questions)
        return {"message": f"成功导入 {count} 道题目", "count": count}
    except HTTPException:
        raise
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"JSON 解析失败: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"题库导入失败: {str(e)}")


@router.get("/question-bank-stats")
async def question_bank_stats():
    try:
        stats = get_question_bank_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取题库统计失败: {str(e)}")
