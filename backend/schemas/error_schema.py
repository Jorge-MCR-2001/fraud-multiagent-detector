from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    status: str = "error"
    error_code: str
    message: str
    trace_id: str
    details: Optional[Dict[str, Any]] = Field(default_factory=dict)