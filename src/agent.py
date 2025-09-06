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

from src.models import DecisionType, Policy, Evidence, ArbitrationDecision

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
    context: Optional[RunContext]


# --- AGENT ---

arbiter_agent = Agent(
    name="Policy Arbiter Agent",
    model="gpt-5-mini-2025-08-07",
    deps_type=ArbiterDependency,
    output_type=ArbitrationDecision
)

@arbiter_agent.system_prompt
async def get_system_prompt(ctx: RunContext[ArbiterDependency]) -> str:
    return f"""
    You are a policy arbiter agent. Your task is to evaluate opposers responses for the following policy.
    You can ask clarifying questions if needed.
    You will be provided with the policy and evidences of the defendent of the policy.

    Policy:
    {ctx.deps.policy}

    Defender Evidence:
    {ctx.deps.defender_evidences}

    Opposer Evidence:
    {ctx.deps.opposer_evidences}

    Context:
    {ctx.deps.context.messages}
    """

# --- TOOLS IMPLEMENTATIONS ---

@arbiter_agent.tool
async def request_opposer_evidence(ctx: RunContext[ArbiterDependency], question: str) -> str:
    """
    Request additional evidence from the opposer during arbitration.

    This tool allows the arbiter agent to gather more information from users
    who oppose a policy when the initial evidence is insufficient for making
    a decision. The tool simulates an interactive evidence gathering process.

    Args:
        ctx (RunContext[ArbiterDependency]): The runtime context containing
            arbitration state and policy information.
        question (str): The specific question to ask the opposer. Should be
            clear, focused, and directly related to the policy dispute.

    Returns:
        str: The opposer's response to the question. In the current implementation,
            this returns a simulated response for testing purposes.

    Note:
        This is currently implemented as a simulation. In production, this would
        interface with a user notification system to collect real responses.
    """
    # Simulate asking the opposer for more evidence
    await asyncio.sleep(1)
    return f"Simulated response to '{question}' from opposer."

@arbiter_agent.tool
async def request_defender_evidence(ctx: RunContext[ArbiterDependency], question: str) -> str:
    """
    Request additional evidence from the defender during arbitration.

    This tool allows the arbiter agent to gather more information from users
    who defend a policy when the initial evidence is insufficient for making
    a decision. The tool simulates an interactive evidence gathering process.

    Args:
        ctx (RunContext[ArbiterDependency]): The runtime context containing
            arbitration state and policy information.
        question (str): The specific question to ask the defender. Should be
            clear, focused, and directly related to the policy defense.

    Returns:
        str: The defender's response to the question. In the current implementation,
            this returns a simulated response for testing purposes.

    Note:
        This is currently implemented as a simulation. In production, this would
        interface with a user notification system to collect real responses.
    """
    # Simulate asking the defender for more evidence
    await asyncio.sleep(1)
    return f"Simulated response to '{question}' from defender."