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

load_dotenv()

# --- AGENT ---

arbiter_agent = Agent(
    name="Policy Arbiter Agent",
    model="gpt-5-mini-2025-08-07",
)

@arbiter_agent.system_prompt
async def get_system_prompt() -> str:
    return f"""

    """

# --- TOOLS IMPLEMENTATIONS ---

