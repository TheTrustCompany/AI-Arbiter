"""
Policy Arbiter Agent and Tools

This module implements an AI-powered policy arbitration system using Pydantic AI.
The agent evaluates policies based on evidence from both opposers and defenders,
making informed decisions about policy disputes.

Key Components:
    - ArbiterDependency: Data structure containing policy and evidence context
    - arbiter_agent: Main AI agent for policy arbitration decisions
    - Tool functions: request_opposer_evidence, request_defender_evidence

"""

from dotenv import load_dotenv
import os
import json
from typing import List, Optional
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, UUID4, conint, constr
from pydantic_ai import Agent, RunContext
from dataclasses import dataclass
import asyncio

from models import DecisionType, Policy, Evidence, ArbitrationDecision

load_dotenv()


@dataclass
class ArbiterDependency:
    """
    Dependencies for the Arbiter Agent containing all necessary context for policy evaluation.

    This class encapsulates all the data required by the arbiter agent to make informed
    decisions about policy disputes. It includes the policy under review, evidence from
    both sides of the dispute, and any additional runtime context.

    Attributes:
        policy (Policy): The policy being evaluated for arbitration. Contains policy
            details including ID, name, description, and creation metadata.
        opposer_evidences (List[Evidence]): List of evidence submissions from users
            opposing the policy. Each evidence contains content, submitter ID, and timestamps.
        defender_evidences (List[Evidence]): List of evidence submissions from users
            defending the policy. Each evidence contains content, submitter ID, and timestamps.
        context (Optional[RunContext]): Optional runtime context containing conversation
            history and additional metadata for the current arbitration session.

    """
    policy: Policy
    opposer_evidences: List[Evidence]
    defender_evidences: List[Evidence]


# --- AGENT ---

arbiter_agent = Agent(
    name="Policy Arbiter Agent",
    model="gpt-5-mini-2025-08-07",
    deps_type=ArbiterDependency,
    output_type=ArbitrationDecision
)

@arbiter_agent.system_prompt
async def get_system_prompt(ctx: RunContext[ArbiterDependency]) -> str:
    _prompt = f"""
    You are a policy arbiter agent. 
    Your task is to evaluate Policy and Evidence provided by both opposer and defender. To check wheater defender has neglected the policy or not.
    You can ask clarifying questions if needed.
    You will be provided with the policy and evidences of the defendent of the policy.

    Policy is a set of rules or guidelines or facts that have been agreed upon by both oppeser and defender.
    Evidence is a piece of information or argument or proof that has been fact checked to be correct.

    Always reason step by step and provide a final decision at the end.
    Make sure to consider all evidence provided before making a decision.
    You can ask for evidence for both sides if you need more information.

    Your final decision should be one of the following:
    - APPROVE: The policy is valid and should be upheld.
    - REJECT: The policy is invalid and should be overturned.
    - CLEARIFY: Use this if you don't want to make a decision yet. Ask questions to gather more information about the problem.
    - REQUEST_OPPOSER_EVIDENCE: The Opposer needs to provide more evidence to support their claim.
    - REQUEST_DEFENDER_EVIDENCE: The defender's case has potential merit but requires additional evidence or clarification to properly evaluate.

    Don't make up evidence. Only use the evidence provided.
    Be objective and impartial in your evaluation.
    Be concise and clear in your reasoning.

    Don't take action if you don't have to.(use DecisionType as CLEARIFY if you don't want to take action)

    message should be the response to the user from arbiter.

    When making your decision, provide a confidence level between 0.0 and 1.0 indicating how certain you are about your decision.
    Also provide a detailed reasoning for your decision.
    
    """
    _prompt += f"""
    Policy:
    """
    _prompt += f"""
    {ctx.deps.policy}
    """

    _prompt += f"""
    Defender Evidence:
    """
    for evidence in ctx.deps.defender_evidences:
        _prompt += f"""
        - {evidence.content} (submitted by {evidence.submitter_id} at {evidence.created_at})
        """

    _prompt += f"""
    Opposer Evidence:
    """
    for evidence in ctx.deps.opposer_evidences:
        _prompt += f"""
        - {evidence.content} (submitted by {evidence.submitter_id} at {evidence.created_at})
        """

    _prompt += f"""
    Context:
    {ctx.messages}
    """
    return _prompt
# --- TOOLS IMPLEMENTATIONS ---

#Tools will be implemented in the future

