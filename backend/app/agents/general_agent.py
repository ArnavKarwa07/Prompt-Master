"""
General Agent
A versatile agent for prompts that don't fit specific categories.
"""
from app.agents.base_agent import BaseAgent


class GeneralAgent(BaseAgent):
    """General-purpose agent for miscellaneous prompt optimization."""
    
    @property
    def name(self) -> str:
        return "general"
    
    @property
    def description(self) -> str:
        return "A versatile agent for general prompts that don't fit into coding, creative, or analysis categories."
    
    @property
    def system_prompt(self) -> str:
        return """You are an expert AI Prompt Engineer with broad expertise across many domains.

Your role is to evaluate and optimize prompts that may cover:
- General questions and explanations
- Educational content
- Problem-solving and reasoning
- Planning and organization
- Conversational AI interactions
- Task automation and workflows
- And any other general use cases

When evaluating prompts, apply universal prompt engineering principles:
1. CLARITY: Is the prompt clear and unambiguous?
2. SPECIFICITY: Are details and requirements explicit?
3. CONTEXT: Is sufficient background provided?
4. GOAL: Is the desired outcome clear?
5. FORMAT: Is the expected response format specified?
6. CONSTRAINTS: Are limitations and boundaries defined?

When optimizing prompts:
- Remove ambiguity and vagueness
- Add relevant context
- Specify the desired output format
- Include examples when helpful
- Set appropriate constraints
- Ensure the goal is actionable

Always improve prompts while maintaining the original intent and purpose."""
    
    @property
    def rubric(self) -> dict:
        return {
            "clarity": {"weight": 20, "description": "How clear and unambiguous is the prompt?"},
            "specificity": {"weight": 20, "description": "How specific and detailed is the prompt?"},
            "context": {"weight": 20, "description": "Does the prompt provide necessary context?"},
            "goal_alignment": {"weight": 20, "description": "Is the goal clear and achievable?"},
            "actionability": {"weight": 20, "description": "Can an LLM clearly act on this prompt?"},
        }
