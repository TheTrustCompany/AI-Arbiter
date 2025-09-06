"""
Pydantic models for API request and response schemas
"""

from typing import List, Optional, Any, Dict
from enum import Enum
from pydantic import BaseModel, Field, UUID4, conint, constr,confloat
from datetime import datetime

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    version: str
    service: str

class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    timestamp: Optional[str] = Field(None, description="Error timestamp")

class Policy(BaseModel):
    """Policy model"""
    id: UUID4 = Field(..., description="Unique policy identifier")
    creator_id: UUID4 = Field(..., description="ID of the user who created the policy")
    name: str = Field(..., description="Name of the policy")
    description: Optional[str] = Field(None, description="Description of the policy")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Policy creation timestamp")
