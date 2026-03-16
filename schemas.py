from pydantic import BaseModel
from typing import List, Optional

class ThreatRequest(BaseModel):
    content: str
    content_type: str  # "email", "message", "url", "deepfake", "behavior", "ai", "prompt"

class Recommendation(BaseModel):
    action: str
    description: str

class ThreatResponse(BaseModel):
    threat_type: str
    risk_score: int  # 0–100
    explanation: List[str]
    detected_patterns: List[str]
    recommendations: List[Recommendation]
    full_report: Optional[str] = None
