import json
import time
from pathlib import Path


class RAGLogger:
    def __init__(self, log_dir: str = "logs/rag"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def log_query(
        self,
        stage: str,
        query_text: str | None,
        results: list[dict],
        distances: list[float] | None = None,
        job_type: str | None = None,
        k: int = 2,
    ):
        entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "stage": stage,
            "job_type": job_type,
            "query_text": (query_text[:300] if query_text else None),
            "k": k,
            "num_results": len(results),
            "results": [
                {
                    "question": r.get("question", "")[:100],
                    "category": r.get("category", ""),
                    "distance": distances[i] if distances and i < len(distances) else None,
                }
                for i, r in enumerate(results[:5])
            ],
        }

        log_file = self.log_dir / f"rag_{time.strftime('%Y%m%d')}.jsonl"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def log_upload(self, count: int, job_type: str | None = None):
        entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "event": "upload",
            "count": count,
            "job_type": job_type,
        }

        log_file = self.log_dir / f"rag_{time.strftime('%Y%m%d')}.jsonl"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def log_seed(self, count: int):
        entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "event": "seed",
            "count": count,
        }

        log_file = self.log_dir / f"rag_{time.strftime('%Y%m%d')}.jsonl"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def log_performance(
        self,
        stage: str,
        elapsed_ms: float,
        asked_count: int,
        result_count: int,
    ):
        entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "event": "performance",
            "stage": stage,
            "elapsed_ms": round(elapsed_ms, 2),
            "asked_count": asked_count,
            "result_count": result_count,
        }

        log_file = self.log_dir / f"rag_{time.strftime('%Y%m%d')}.jsonl"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


_rag_logger: RAGLogger | None = None


def get_rag_logger() -> RAGLogger:
    global _rag_logger
    if _rag_logger is None:
        _rag_logger = RAGLogger()
    return _rag_logger
