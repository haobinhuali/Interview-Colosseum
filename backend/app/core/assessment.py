from pydantic import BaseModel, field_validator


class TechAssessment(BaseModel):
    tech_depth: int
    integrity_flag: str
    communication: int

    @field_validator("tech_depth", "communication")
    @classmethod
    def validate_score(cls, v):
        if not 1 <= v <= 10:
            raise ValueError("分数必须在 1-10 之间")
        return v

    @field_validator("integrity_flag")
    @classmethod
    def validate_flag(cls, v):
        if v not in ("honest", "evasive", "dishonest"):
            raise ValueError("诚实度标记必须是 honest/evasive/dishonest")
        return v


class PressureAssessment(BaseModel):
    pressure_resistance: int
    stress_style: str

    @field_validator("pressure_resistance")
    @classmethod
    def validate_score(cls, v):
        if not 1 <= v <= 10:
            raise ValueError("分数必须在 1-10 之间")
        return v

    @field_validator("stress_style")
    @classmethod
    def validate_style(cls, v):
        if v not in ("calm", "defensive", "agitated"):
            raise ValueError("风格必须是 calm/defensive/agitated")
        return v


class ComprehensiveAssessment(BaseModel):
    recovery: int
    knowledge_transfer: int

    @field_validator("recovery", "knowledge_transfer")
    @classmethod
    def validate_score(cls, v):
        if not 1 <= v <= 10:
            raise ValueError("分数必须在 1-10 之间")
        return v


_ASSESSMENT_MODELS = {
    "TECH": TechAssessment,
    "PRESSURE": PressureAssessment,
    "COMPREHENSIVE": ComprehensiveAssessment,
}


def validate_assessment(stage: str, data: dict) -> dict | None:
    model = _ASSESSMENT_MODELS.get(stage)
    if not model or not data:
        return None
    try:
        return model(**data).model_dump()
    except Exception:
        return None
