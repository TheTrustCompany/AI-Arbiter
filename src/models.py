"""
Pydantic models for API request and response schemas

This module defines all data models used throughout the AI Arbiter system,
including API schemas, agent data structures, and decision models. All models
use Pydantic for validation and serialization.

Model Categories:
    - API Models: HealthResponse, ErrorResponse
    - Core Agent Models: Policy, Evidence, ArbitrationDecision
    - Enums: DecisionType

These models ensure type safety and data validation across the arbitration
system, from API endpoints to agent processing.
"""

from typing import List, Optional, Any, Dict
from enum import Enum
from pydantic import BaseModel, Field, UUID4, conint, constr,confloat

from datetime import datetime

# --- API DATA MODELS---

class HealthResponse(BaseModel):
    """
    Health check response model for API monitoring.

    This model provides a standard format for health check endpoints,
    allowing monitoring systems to verify service availability and version.

    Attributes:
        status (str): Current service status (e.g., "healthy", "degraded", "unhealthy").
        version (str): Current version of the service for deployment tracking.
        service (str): Name of the service for identification in multi-service environments.
    """
    status: str
    version: str
    service: str

class ErrorResponse(BaseModel):
    """
    Standard error response model for API endpoints.

    This model provides a consistent error response format across all API
    endpoints, enabling standardized error handling and debugging.

    Attributes:
        detail (str): Human-readable error message describing what went wrong.
            Required field that should provide actionable information to users.
        error_code (Optional[str]): Machine-readable error code for programmatic
            error handling. Optional but recommended for client applications.
        timestamp (Optional[str]): ISO 8601 timestamp when the error occurred,
            useful for debugging and log correlation.
    """
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    timestamp: Optional[str] = Field(None, description="Error timestamp")


# --- AGENT DATA MODELS---

class Policy(BaseModel):
    """
    Policy model representing a policy subject to arbitration.

    This model defines the structure of policies that can be disputed and
    evaluated by the arbiter agent. Policies are created by users and can
    be challenged by opponents who submit evidence against them.

    Attributes:
        id (UUID4): Unique policy identifier for database references and tracking.
        creator_id (UUID4): ID of the user who created the policy, used for
            accountability and permission checks.
        name (str): Human-readable name of the policy, should be descriptive
            and unique within the system context.
        description (Optional[str]): Detailed description of the policy including
            its purpose, scope, and implementation details. Optional but recommended.
        created_at (datetime): Timestamp when the policy was created, automatically
            set to UTC time at creation.

    """
    id: UUID4 = Field(..., description="Unique policy identifier")
    creator_id: UUID4 = Field(..., description="ID of the user who created the policy")
    name: str = Field(..., description="Name of the policy")
    description: Optional[str] = Field(None, description="Description of the policy")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Policy creation timestamp")

class Evidence(BaseModel):
    """
    Evidence model representing submissions in policy arbitration.

    This model captures evidence submitted by both opposers and defenders
    during policy disputes. Evidence forms the basis for agent decision-making
    and provides transparency in the arbitration process.

    Attributes:
        id (UUID4): Unique evidence identifier for tracking and referencing
            specific pieces of evidence in decisions.
        policy_id (UUID4): ID of the policy this evidence relates to, establishing
            the connection between evidence and the disputed policy.
        submitter_id (UUID4): ID of the user who submitted this evidence, used
            for tracking participation and preventing spam.
        content (str): The actual evidence content including facts, arguments,
            documentation, or other relevant information.
        created_at (datetime): Timestamp when the evidence was submitted,
            automatically set to UTC time at submission.

    """
    id: UUID4 = Field(..., description="Unique evidence identifier")
    policy_id: UUID4 = Field(..., description="ID of the associated policy")
    submitter_id: UUID4 = Field(..., description="ID of the user who submitted the evidence")
    content: str = Field(..., description="Content of the evidence")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Evidence submission timestamp")

class DecisionType(str, Enum):
    """
    Enumeration of decision types available to the arbiter agent.

    This enum defines all possible decision outcomes that the arbiter agent
    can make when evaluating policy disputes. Each decision type represents
    a specific conclusion about the validity of opposition claims.

    Values:
        APPROVE_OPPOSER: The opposition has provided sufficient valid evidence
            to successfully challenge the policy. The policy should be rejected
            or modified based on the opposition's claims.
        
        REJECT_OPPOSER: The opposition has failed to provide sufficient evidence
            to challenge the policy. The policy should remain in effect as
            the defender's evidence is stronger or the opposition is unfounded.
        
        NEEDS_MORE_INFO: There is insufficient evidence from both sides to make
            a definitive decision. More information is required before proceeding.
            Use this type if you don't want to make a decision or take action yet.
        
        REQUEST_OPPOSER_EVIDENCE: The opposer's case has potential merit but
            requires additional evidence or clarification to properly evaluate.
        
        REQUEST_DEFENDER_EVIDENCE: The defense needs to provide additional
            evidence to counter the opposition's claims effectively.

    Usage:
        These decision types guide the agent's reasoning process and determine
        the next steps in the arbitration workflow.
    """
    APPROVE_OPPOSER = "approve_opposer"
    REJECT_OPPOSER = "reject_opposer"
    NEEDS_MORE_INFO = "needs_more_info"
    REQUEST_OPPOSER_EVIDENCE = "request_opposer_evidence"
    REQUEST_DEFENDER_EVIDENCE = "request_defender_evidence"

class ArbitrationDecision(BaseModel):
    """
    Arbitration decision model representing the agent's final judgment.

    This model captures the complete decision made by the arbiter agent after
    evaluating a policy dispute. It includes the decision itself, supporting
    reasoning, confidence metrics, and all necessary metadata for transparency
    and accountability.

    Attributes:
        id (UUID4): Unique decision identifier for tracking and referencing
            specific arbitration outcomes.
        policy_id (UUID4): ID of the policy that was evaluated, linking the
            decision back to the original dispute context.
        opposer_id (UUID4): ID of the user who opposed the policy, required
            for notification and record-keeping purposes.
        defender_id (UUID4): ID of the user who defended the policy, typically
            the policy creator but may be a designated defender.
        decision_type (DecisionType): The type of decision made, selected from
            the predefined DecisionType enum values.
        decision (str): Human-readable explanation of the decision, providing
            clear communication of the outcome to all parties.
        confidence (float): Numerical confidence level of the decision ranging
            from 0.0 (no confidence) to 1.0 (complete confidence). Used to
            indicate the strength of the agent's conviction.
        reasoning (str): Detailed explanation of the reasoning process behind
            the decision, including analysis of evidence and logical deductions.
        created_at (datetime): Timestamp when the decision was made, automatically
            set to UTC time at decision creation.

    """
    id: UUID4 = Field(..., description="Unique decision identifier")
    policy_id: UUID4 = Field(..., description="ID of the associated policy")
    opposer_id: UUID4 = Field(..., description="ID of the opposer")
    defender_id: UUID4 = Field(..., description="ID of the defender")
    decision_type: DecisionType = Field(..., description="Type of decision made")
    decision: str = Field(..., description="Decision made by the arbiter")
    confidence: confloat(ge=0.0, le=1.0) = Field(..., description="Confidence level of the decision (0.0 to 1.0)")
    reasoning: str = Field(None, description="Reasoning behind the decision")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Decision timestamp")