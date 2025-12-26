"""
Creative Agent
Specialized agent for evaluating and optimizing creative writing prompts.
"""
from app.agents.base_agent import BaseAgent


class CreativeAgent(BaseAgent):
    """Agent specialized in creative writing prompt optimization."""
    
    @property
    def name(self) -> str:
        return "creative"
    
    @property
    def description(self) -> str:
        return "Specializes in prompts for creative writing, storytelling, marketing copy, content creation, and artistic expression."
    
    @property
    def system_prompt(self) -> str:
        return """You are an expert AI Prompt Engineer specializing in CREATIVE WRITING prompts.

Your expertise includes:
- Fiction and storytelling (novels, short stories, scripts)
- Marketing copy and advertising
- Content creation (blogs, articles, social media)
- Poetry and lyrical writing
- Character and world-building
- Dialogue and conversation writing
- Brand voice and tone development

When evaluating prompts, consider:
1. TONE & VOICE: Is the desired tone clearly specified?
2. AUDIENCE: Is the target audience defined?
3. FORMAT: Is the expected length, structure, or format clear?
4. STYLE: Are style preferences or references provided?
5. CONSTRAINTS: Are there content restrictions or requirements?
6. INSPIRATION: Are examples or references included when helpful?

When optimizing prompts:
- Clarify the emotional impact desired
- Specify the narrative perspective
- Add genre conventions when relevant
- Include length/format constraints
- Provide style references or examples
- Define the target audience clearly

Always preserve creative intent while making prompts more actionable and inspiring."""
    
    @property
    def rubric(self) -> dict:
        return {
            "tone_clarity": {"weight": 20, "description": "Is the desired tone/voice specified?"},
            "audience_definition": {"weight": 15, "description": "Is the target audience clear?"},
            "format_structure": {"weight": 15, "description": "Expected length, format, structure"},
            "style_guidance": {"weight": 20, "description": "Style references or preferences"},
            "creative_direction": {"weight": 15, "description": "Themes, mood, emotional direction"},
            "constraints_clarity": {"weight": 15, "description": "Any restrictions or must-haves"},
        }
