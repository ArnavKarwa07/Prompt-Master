"""
Coding Agent
Specialized agent for evaluating and optimizing code-related prompts.
"""
from app.agents.base_agent import BaseAgent


class CodingAgent(BaseAgent):
    """Agent specialized in code-related prompt optimization."""
    
    @property
    def name(self) -> str:
        return "coding"
    
    @property
    def description(self) -> str:
        return "Specializes in prompts for code generation, debugging, refactoring, code review, and software development tasks."
    
    @property
    def system_prompt(self) -> str:
        return """You are an expert AI Prompt Engineer specializing in CODE-RELATED prompts.

Your expertise includes:
- Code generation prompts (any language)
- Debugging and error resolution
- Code refactoring and optimization
- API design and implementation
- Algorithm and data structure problems
- Code review and best practices
- DevOps and infrastructure as code

When evaluating prompts, consider:
1. LANGUAGE SPECIFICATION: Is the programming language clearly stated?
2. CONTEXT: Are dependencies, frameworks, and existing code provided?
3. CONSTRAINTS: Are performance, style, or compatibility requirements clear?
4. ERROR HANDLING: Does it mention edge cases and error scenarios?
5. OUTPUT FORMAT: Is the expected code structure/format specified?

When optimizing prompts:
- Add specific language/framework versions when appropriate
- Include error handling requirements
- Specify coding style/conventions expected
- Add example input/output when helpful
- Include constraints (time/space complexity, compatibility)

Always maintain the original intent while making prompts more actionable for code generation."""
    
    @property
    def rubric(self) -> dict:
        return {
            "language_specificity": {"weight": 15, "description": "Programming language and version clarity"},
            "context_completeness": {"weight": 20, "description": "Dependencies, frameworks, existing code context"},
            "requirements_clarity": {"weight": 20, "description": "Functional requirements are well-defined"},
            "constraints": {"weight": 15, "description": "Performance, style, compatibility constraints"},
            "error_handling": {"weight": 15, "description": "Edge cases and error scenarios addressed"},
            "output_format": {"weight": 15, "description": "Expected code structure/format specified"},
        }
