"""
Supervisor Module
Routes prompts to the appropriate specialized agent using LLM-based classification.
"""
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Literal
import json

from app.core.config import get_settings
from app.agents import AGENT_REGISTRY


AgentType = Literal["coding", "creative", "analyst", "general"]


class Supervisor:
    """
    Supervisor that routes prompts to specialized agents.
    Uses the secondary (faster) model for quick classification.
    """
    
    def __init__(self):
        settings = get_settings()
        # Use the faster model for routing decisions
        self.llm = ChatGroq(
            api_key=settings.groq_api_key,
            model_name=settings.secondary_model,
            temperature=0,
        )
        
        # Build agent descriptions for the prompt
        self.agent_descriptions = "\n".join([
            f"- {name}: {cls().description}"
            for name, cls in AGENT_REGISTRY.items()
        ])
    
    @property
    def system_prompt(self) -> str:
        return f"""You are a prompt classification system. Your job is to analyze a user's prompt and determine which specialized agent should handle it.

Available agents:
{self.agent_descriptions}

Analyze the prompt and user's goal, then select the most appropriate agent.

Respond with ONLY a JSON object in this format:
{{"agent": "<agent_name>", "confidence": <0.0-1.0>, "reasoning": "<brief explanation>"}}

Rules:
1. Choose "coding" for any programming, debugging, or software-related tasks
2. Choose "creative" for writing, marketing, storytelling, or artistic content
3. Choose "analyst" for data analysis, research, reports, or analytical tasks
4. Choose "general" for prompts that don't clearly fit the above categories
5. Confidence should reflect how certain you are about the classification"""
    
    async def classify(self, prompt: str, goal: str) -> dict:
        """
        Classify a prompt and return the recommended agent.
        
        Returns:
            dict with keys: agent, confidence, reasoning
        """
        user_message = f"""
PROMPT TO CLASSIFY:
"{prompt}"

USER'S GOAL:
"{goal}"

Select the appropriate agent and explain your reasoning.
"""
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=user_message)
        ]
        
        try:
            response = await self.llm.ainvoke(messages)
            content = response.content
            
            # Extract JSON from response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            result = json.loads(content.strip())
            
            # Validate agent type
            agent = result.get("agent", "general").lower()
            if agent not in AGENT_REGISTRY:
                agent = "general"
            
            return {
                "agent": agent,
                "confidence": result.get("confidence", 0.8),
                "reasoning": result.get("reasoning", "Default classification")
            }
            
        except Exception as e:
            # Fallback to general agent on error
            return {
                "agent": "general",
                "confidence": 0.5,
                "reasoning": f"Fallback due to classification error: {str(e)}"
            }


# Singleton instance
_supervisor = None


def get_supervisor() -> Supervisor:
    """Get or create the supervisor singleton."""
    global _supervisor
    if _supervisor is None:
        _supervisor = Supervisor()
    return _supervisor
