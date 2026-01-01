"""
Base Agent Module
Defines the abstract base class for all specialized agents.
"""
from abc import ABC, abstractmethod
from typing import TypedDict, Annotated, Optional, Any
from pydantic import BaseModel
from langchain_groq import ChatGroq
from app.core.config import get_settings


class AgentState(TypedDict):
    """Shared state across all agents in the graph."""
    prompt: str
    goal: str
    context: Optional[str]
    agent_type: Optional[str]
    score: Optional[int]
    feedback: Optional[str]
    optimized_prompt: Optional[str]
    rag_context: Optional[str]
    project_context: Optional[str]  # Context from uploaded project files
    error: Optional[str]


class AgentResponse(BaseModel):
    """Standard response from any agent."""
    score: int
    feedback: str
    optimized_prompt: str
    rubric_breakdown: dict


class BaseAgent(ABC):
    """Abstract base class for all specialized agents."""
    
    def __init__(self, model_name: Optional[str] = None):
        settings = get_settings()
        self.model_name = model_name or settings.primary_model
        self.llm = ChatGroq(
            api_key=settings.groq_api_key,
            model_name=self.model_name,
            temperature=0.3,
        )
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Agent identifier name."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Agent description for supervisor routing."""
        pass
    
    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """The system prompt defining this agent's expertise."""
        pass
    
    @property
    def rubric(self) -> dict:
        """Scoring rubric for this agent type."""
        return {
            "clarity": {"weight": 20, "description": "How clear and unambiguous is the prompt?"},
            "specificity": {"weight": 20, "description": "How specific and detailed is the prompt?"},
            "context": {"weight": 20, "description": "Does the prompt provide necessary context?"},
            "goal_alignment": {"weight": 20, "description": "How well does it align with the stated goal?"},
            "actionability": {"weight": 20, "description": "Can an LLM clearly act on this prompt?"},
        }
    
    def build_evaluation_prompt(self, prompt: str, goal: str, context: str = "", project_context: str = "") -> str:
        """Build the evaluation prompt for this agent."""
        rubric_text = "\n".join([
            f"- {key} ({v['weight']} points): {v['description']}"
            for key, v in self.rubric.items()
        ])
        
        kb_context = ""
        if context:
            kb_context = f"""
KNOWLEDGE BASE REFERENCE:
Use the following prompt engineering best practices to inform your evaluation and optimization:
---
{context}
---
Apply these techniques when optimizing the prompt. Reference specific techniques in your feedback.
"""
        
        proj_context = ""
        if project_context:
            proj_context = f"""
PROJECT FILES CONTEXT:
The user has uploaded the following files to their project. Use this context to better understand their domain and provide more relevant optimization:
---
{project_context}
---
"""
        
        return f"""
You are evaluating a prompt for: {goal}

PROMPT TO EVALUATE:
\"\"\"
{prompt}
\"\"\"
{kb_context}{proj_context}
SCORING RUBRIC (Total: 100 points):
{rubric_text}

Provide your response in this exact JSON format:
{{
    "score": <total_score_0_to_100>,
    "rubric_breakdown": {{
        "clarity": <score>,
        "specificity": <score>,
        "context": <score>,
        "goal_alignment": <score>,
        "actionability": <score>
    }},
    "feedback": "<detailed feedback explaining the scores>",
    "optimized_prompt": "<your improved version of the prompt>"
}}

Be thorough and constructive in your feedback. The optimized prompt should be significantly better.
"""
    
    async def evaluate(self, state: AgentState) -> AgentState:
        """Evaluate and optimize the prompt."""
        try:
            prompt = state["prompt"]
            goal = state["goal"]
            context = state.get("rag_context", "")
            project_context = state.get("project_context", "")
            
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": self.build_evaluation_prompt(prompt, goal, context, project_context)}
            ]
            
            response = await self.llm.ainvoke(messages)
            
            # Parse the JSON response
            import json
            import re
            content = response.content
            
            # Extract JSON from response - try multiple methods
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            # Try to find JSON object in content
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                content = json_match.group(0)
            
            # Clean up common JSON issues
            content = content.strip()
            # Replace any unescaped newlines in strings
            content = re.sub(r'(?<!\\)\n(?=.*")', '\\n', content)
            
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                # Try to fix common issues with single quotes or trailing commas
                content = re.sub(r",\s*}", "}", content)
                content = re.sub(r",\s*\]", "]", content)
                result = json.loads(content)
            
            return {
                **state,
                "agent_type": self.name,
                "score": result.get("score", 0),
                "feedback": result.get("feedback", ""),
                "optimized_prompt": result.get("optimized_prompt", ""),
            }
            
        except Exception as e:
            return {
                **state,
                "agent_type": self.name,
                "error": str(e),
                "score": 0,
                "feedback": f"Error during evaluation: {str(e)}",
                "optimized_prompt": state["prompt"],
            }
