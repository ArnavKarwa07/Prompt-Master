"""Agents module exports."""
from app.agents.base_agent import BaseAgent, AgentState, AgentResponse
from app.agents.coding_agent import CodingAgent
from app.agents.creative_agent import CreativeAgent
from app.agents.analyst_agent import AnalystAgent
from app.agents.general_agent import GeneralAgent

__all__ = [
    "BaseAgent",
    "AgentState",
    "AgentResponse",
    "CodingAgent",
    "CreativeAgent",
    "AnalystAgent",
    "GeneralAgent",
]

# Agent registry for easy lookup
AGENT_REGISTRY = {
    "coding": CodingAgent,
    "creative": CreativeAgent,
    "analyst": AnalystAgent,
    "general": GeneralAgent,
}


def get_agent(agent_type: str) -> BaseAgent:
    """Get an agent instance by type."""
    agent_class = AGENT_REGISTRY.get(agent_type.lower(), GeneralAgent)
    return agent_class()


def get_all_agents() -> dict[str, BaseAgent]:
    """Get all agent instances."""
    return {name: cls() for name, cls in AGENT_REGISTRY.items()}
