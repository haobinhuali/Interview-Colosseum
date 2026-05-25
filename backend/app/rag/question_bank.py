import os
import time
from pathlib import Path
from typing import TypedDict

import chromadb

from app.rag.seed_data import SEED_QUESTIONS
from app.rag.rag_logger import get_rag_logger

_CHROMA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "chroma_db")
_COLLECTION_NAME = "interview_questions"


class RAGQueryResult(TypedDict):
    ids: list[str]
    texts: list[str]


class RAGQuestionBank:
    def __init__(self):
        Path(_CHROMA_DIR).mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=_CHROMA_DIR)
        self.collection = self.client.get_or_create_collection(
            name=_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        self.logger = get_rag_logger()
        if self.collection.count() == 0:
            self._seed_questions()

    def _seed_questions(self):
        batch_size = 500
        for start in range(0, len(SEED_QUESTIONS), batch_size):
            batch = SEED_QUESTIONS[start:start + batch_size]
            documents = []
            metadatas = []
            ids = []
            for q in batch:
                doc = f"{q['category']}: {q['question']}"
                documents.append(doc)
                metadatas.append({
                    "stage": q["stage"],
                    "category": q["category"],
                    "job_type": q["job_type"],
                    "question": q["question"],
                    "reference_answer": q["reference_answer"],
                })
                ids.append(str(q["id"]))
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
            )
        self.logger.log_seed(len(SEED_QUESTIONS))

    def query_questions(
        self,
        job_type: str,
        current_stage: str,
        k: int = 2,
        query_text: str | None = None,
        asked_ids: list[str] | None = None,
    ) -> RAGQueryResult:
        start_time = time.perf_counter()
        search_text = query_text if query_text else f"{current_stage} {job_type}"
        asked_set = set(asked_ids) if asked_ids else set()
        collection_count = self.collection.count()
        fetch_n = min(max(k + len(asked_set), k * 3, 5), collection_count)

        where_filter = {"stage": current_stage}
        if job_type:
            where_filter = {"$and": [{"stage": current_stage}, {"job_type": job_type}]}

        results = self._do_query(search_text, fetch_n, where_filter)

        metadatas = results["metadatas"][0] if results["metadatas"] else []
        distances = results["distances"][0] if results["distances"] else []
        result_ids = results["ids"][0] if results["ids"] else []

        self.logger.log_query(
            stage=current_stage,
            query_text=query_text,
            results=metadatas,
            distances=distances,
            job_type=job_type,
            k=k,
        )

        filtered_ids: list[str] = []
        filtered_texts: list[str] = []
        for i, m in enumerate(metadatas):
            qid = result_ids[i] if i < len(result_ids) else ""
            if qid in asked_set:
                continue
            filtered_ids.append(qid)
            filtered_texts.append(
                f"类别：{m['category']}\n"
                f"阶段：{m['stage']}\n"
                f"岗位：{m['job_type']}\n"
                f"问题：{m['question']}\n"
                f"参考答案：{m['reference_answer']}"
            )
            if len(filtered_ids) >= k:
                break

        if not filtered_ids and metadatas:
            for i, qid in enumerate(result_ids):
                if qid not in asked_set:
                    m = metadatas[i]
                    filtered_ids = [qid]
                    filtered_texts = [
                        f"类别：{m['category']}\n"
                        f"阶段：{m['stage']}\n"
                        f"岗位：{m['job_type']}\n"
                        f"问题：{m['question']}\n"
                        f"参考答案：{m['reference_answer']}"
                    ]
                    break

        if not filtered_ids:
            filtered_ids = []
            filtered_texts = ["标准题库已耗尽，请基于简历自由追问"]

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        self.logger.log_performance(
            stage=current_stage,
            elapsed_ms=elapsed_ms,
            asked_count=len(asked_set),
            result_count=len(filtered_ids)
        )

        return RAGQueryResult(ids=filtered_ids, texts=filtered_texts)

    def _do_query(self, search_text: str, n_results: int, where_filter: dict) -> dict:
        try:
            return self.collection.query(
                query_texts=[search_text],
                n_results=n_results,
                where=where_filter,
                include=["metadatas", "distances"],
            )
        except Exception:
            pass

        stage_value = where_filter.get("stage")
        if stage_value:
            try:
                return self.collection.query(
                    query_texts=[search_text],
                    n_results=n_results,
                    where={"stage": stage_value},
                    include=["metadatas", "distances"],
                )
            except Exception:
                pass

        return self.collection.query(
            query_texts=[search_text],
            n_results=n_results,
            include=["metadatas", "distances"],
        )

    def add_questions(self, questions: list[dict]) -> int:
        if not questions:
            return 0

        max_id = self.collection.count()
        documents = []
        metadatas = []
        ids = []
        for i, q in enumerate(questions):
            max_id += 1
            doc = f"{q.get('category', '自定义')}: {q.get('question', '')}"
            documents.append(doc)
            metadatas.append({
                "stage": q.get("stage", "TECH"),
                "category": q.get("category", "自定义"),
                "job_type": q.get("job_type", "通用"),
                "question": q.get("question", ""),
                "reference_answer": q.get("reference_answer", ""),
            })
            ids.append(f"custom_{max_id}_{i}")

        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )

        job_type = questions[0].get("job_type") if questions else None
        self.logger.log_upload(count=len(questions), job_type=job_type)
        return len(questions)

    def get_stats(self) -> dict:
        count = self.collection.count()
        peek = self.collection.peek(limit=1)
        sample_metadata = peek["metadatas"][0] if peek["metadatas"] else {}
        return {
            "total_questions": count,
            "sample_stages": sample_metadata.get("stage", "N/A"),
            "sample_job_type": sample_metadata.get("job_type", "N/A"),
        }


_question_bank: RAGQuestionBank | None = None


def get_question_bank() -> RAGQuestionBank:
    global _question_bank
    if _question_bank is None:
        _question_bank = RAGQuestionBank()
    return _question_bank


def query_questions(
    job_type: str,
    current_stage: str,
    k: int = 2,
    query_text: str | None = None,
    asked_ids: list[str] | None = None,
) -> RAGQueryResult:
    qb = get_question_bank()
    return qb.query_questions(job_type, current_stage, k, query_text, asked_ids)


def add_custom_questions(questions: list[dict]) -> int:
    qb = get_question_bank()
    return qb.add_questions(questions)


def get_question_bank_stats() -> dict:
    qb = get_question_bank()
    return qb.get_stats()
