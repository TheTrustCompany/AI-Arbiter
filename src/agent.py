"""
Policy Arbiter Agent and Tools
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

from src.models import DecisionType, Policy, Proof, ArbitrationDecision

load_dotenv()


@dataclass
class ArbiterDependency:
    """
    Dependencies for the Arbiter Agent.

    Attributes:
        policy (Policy): The policy to be evaluated.
        context (RunContext): The context in which the policy is being evaluated.
    """
    policy: Policy
    opposer_proofs: List[Proof]
    defender_proofs: List[Proof]
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
    You will be provided with the policy and proofs of the defendent of the policy.

    Policy:
    {ctx.deps.policy}

    Defender Evidence:
    {ctx.deps.defender_proofs}

    Opposer Evidence:
    {ctx.deps.opposer_proofs}

    Context:
    {ctx.deps.context.messages}
    """

# --- TOOLS IMPLEMENTATIONS ---

@arbiter_agent.tool
async def request_opposer_proof(ctx: RunContext[ArbiterDependency], question: str) -> str:
    """
    Tool to request additional proof from the opposer.

    Args:
        question (str): The question to ask the opposer.

    Returns:
        str: The response from the opposer.
    """
    # Simulate asking the opposer for more proof
    await asyncio.sleep(1)
    return f"Simulated response to '{question}' from opposer."

@arbiter_agent.tool
async def request_defender_proof(ctx: RunContext[ArbiterDependency], question: str) -> str:
    """
    Tool to request additional proof from the defender.

    Args:
        question (str): The question to ask the defender.

    Returns:
        str: The response from the defender.
    """
    # Simulate asking the defender for more proof
    await asyncio.sleep(1)
    return f"Simulated response to '{question}' from defender."