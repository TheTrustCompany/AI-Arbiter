"""
Pydantic models for API request and response schemas
"""

from typing import List, Optional, Any, Dict
from enum import Enum
from pydantic import BaseModel, Field, UUID4, conint, constr,confloat

from datetime import datetime

# --- API DATA MODELS---

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


# --- AGENT DATA MODELS---

class Policy(BaseModel):
    """Policy model"""
    id: UUID4 = Field(..., description="Unique policy identifier")
    creator_id: UUID4 = Field(..., description="ID of the user who created the policy")
    name: str = Field(..., description="Name of the policy")
    description: Optional[str] = Field(None, description="Description of the policy")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Policy creation timestamp")

class Proof(BaseModel):
    """Proof model"""
    id: UUID4 = Field(..., description="Unique proof identifier")
    policy_id: UUID4 = Field(..., description="ID of the associated policy")
    submitter_id: UUID4 = Field(..., description="ID of the user who submitted the proof")
    content: str = Field(..., description="Content of the proof")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Proof submission timestamp")

class DecisionType(str, Enum):
    """Enumeration of decision types"""
    APPROVE_OPPOSER = "approve_opposer"
    REJECT_OPPOSER = "reject_opposer"
    NEEDS_MORE_INFO = "needs_more_info"
    REQUEST_OPPOSER_PROOF = "request_opposer_proof"
    REQUEST_DEFENDER_PROOF = "request_defender_proof"

class ArbitrationDecision(BaseModel):
    """Arbitration decision model"""
    id: UUID4 = Field(..., description="Unique decision identifier")
    policy_id: UUID4 = Field(..., description="ID of the associated policy")
    opposer_id: UUID4 = Field(..., description="ID of the opposer")
    defender_id: UUID4 = Field(..., description="ID of the defender")
    decision_type: DecisionType = Field(..., description="Type of decision made")
    decision: str = Field(..., description="Decision made by the arbiter")
    confidence: confloat(ge=0.0, le=1.0) = Field(..., description="Confidence level of the decision (0.0 to 1.0)")
    reasoning: str = Field(None, description="Reasoning behind the decision")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Decision timestamp")