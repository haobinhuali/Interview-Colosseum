import json
import copy
from app.utils.db import save_session, get_session as db_get_session


class ProfileManager:
    def __init__(self, session_id: str, resume_id: str, job_type: str):
        self.session_id = session_id
        self.resume_id = resume_id
        self.job_type = job_type
        self.stage = "INIT"
        self.current_round = 0
        self.profile = {
            "resume": {},
            "tech_assessment": {
                "tech_depth": 0,
                "integrity_flag": "",
                "communication": 0
            },
            "pressure_assessment": {
                "pressure_resistance": 0,
                "stress_style": ""
            },
            "comprehensive_assessment": {
                "recovery": 0,
                "knowledge_transfer": 0
            },
            "dialog_history": [],
            "tech_summary": "",
            "pressure_summary": "",
            "key_tech_dialogs": [],
            "key_pressure_dialogs": [],
            "asked_ids": []
        }

    @classmethod
    def load(cls, session_id: str) -> "ProfileManager | None":
        data = db_get_session(session_id)
        if not data:
            return None
        pm = cls(data["session_id"], data["resume_id"], data["job_type"])
        pm.stage = data["stage"]
        pm.current_round = data["current_round"]
        pm.profile = data["profile_data"]
        pm._ensure_fields()
        return pm

    def _ensure_fields(self):
        defaults = {
            "resume": {},
            "tech_assessment": {"tech_depth": 0, "integrity_flag": "", "communication": 0},
            "pressure_assessment": {"pressure_resistance": 0, "stress_style": ""},
            "comprehensive_assessment": {"recovery": 0, "knowledge_transfer": 0},
            "dialog_history": [],
            "tech_summary": "",
            "pressure_summary": "",
            "comprehensive_summary": "",
            "key_tech_dialogs": [],
            "key_pressure_dialogs": [],
            "key_comprehensive_dialogs": [],
            "asked_ids": [],
        }
        for key, default in defaults.items():
            if key not in self.profile:
                self.profile[key] = copy.deepcopy(default)
            elif isinstance(default, dict) and isinstance(self.profile[key], dict):
                for k, v in default.items():
                    if k not in self.profile[key]:
                        self.profile[key][k] = v

    def set_resume(self, resume_data: dict):
        self.profile["resume"] = resume_data
        self._persist()

    def update_tech(self, assessment: dict):
        self.profile["tech_assessment"] = {
            "tech_depth": assessment.get("tech_depth", 0),
            "integrity_flag": assessment.get("integrity_flag", ""),
            "communication": assessment.get("communication", 0)
        }
        self._persist()

    def update_pressure(self, assessment: dict):
        self.profile["pressure_assessment"] = {
            "pressure_resistance": assessment.get("pressure_resistance", 0),
            "stress_style": assessment.get("stress_style", "")
        }
        self._persist()

    def update_comprehensive(self, assessment: dict):
        self.profile["comprehensive_assessment"] = {
            "recovery": assessment.get("recovery", 0),
            "knowledge_transfer": assessment.get("knowledge_transfer", 0)
        }
        self._persist()

    def add_dialog(self, role: str, content: str, stage: str):
        self.profile["dialog_history"].append({
            "role": role,
            "content": content,
            "stage": stage
        })
        self._persist()

    def get_full_profile(self) -> dict:
        return copy.deepcopy(self.profile)

    def get_dialog_history(self, stage: str | None = None) -> list:
        if stage:
            return [d for d in self.profile["dialog_history"] if d["stage"] == stage]
        return self.profile["dialog_history"]

    def set_stage(self, stage: str):
        self.stage = stage
        self._persist()

    def increment_round(self):
        self.current_round += 1
        self._persist()

    def reset_round(self):
        self.current_round = 0
        self._persist()

    def set_stage_summary(self, stage: str, summary: str):
        self.profile[f"{stage.lower()}_summary"] = summary
        self._persist()

    def get_stage_summary(self, stage: str) -> str:
        return self.profile.get(f"{stage.lower()}_summary", "")

    def get_key_dialogs(self, stage: str, max_items: int = 2) -> list:
        dialog_history = self.get_dialog_history(stage=stage)
        if not dialog_history:
            return []
        key_indices = []
        if len(dialog_history) >= 3:
            key_indices.append(2)
        if len(dialog_history) >= 1:
            key_indices.append(len(dialog_history) - 1)
        key_indices = list(dict.fromkeys(key_indices))
        return [dialog_history[i] for i in key_indices if i < len(dialog_history)]

    def get_asked_ids(self) -> list[str]:
        return self.profile.get("asked_ids", [])

    def add_asked_ids(self, ids: list[str]):
        current = set(self.profile.get("asked_ids", []))
        current.update(ids)
        self.profile["asked_ids"] = list(current)
        self._persist()

    def _persist(self):
        save_session(
            self.session_id,
            self.resume_id,
            self.job_type,
            self.stage,
            self.current_round,
            self.profile
        )
