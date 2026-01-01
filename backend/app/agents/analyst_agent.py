"""
Analyst Agent
Specialized agent for evaluating and optimizing data analysis prompts.
"""
from app.agents.base_agent import BaseAgent


class AnalystAgent(BaseAgent):
    """Agent specialized in data analysis and research prompt optimization."""
    
    @property
    def name(self) -> str:
        return "analyst"
    
    @property
    def description(self) -> str:
        return "Specializes in prompts for data analysis, research, reporting, summarization, and analytical reasoning tasks."
    
    @property
    def system_prompt(self) -> str:
        return """You are an expert AI Prompt Engineer specializing in DATA ANALYSIS and RESEARCH prompts.

Your expertise includes:
- Data analysis and interpretation
- Research synthesis and summarization
- Report generation and formatting
- Statistical analysis requests
- Market research and competitive analysis
- Literature reviews and academic research
- Business intelligence and insights

When evaluating prompts, consider:
1. DATA CONTEXT: Is the data source/format clearly described?
2. ANALYSIS TYPE: Is the type of analysis specified?
3. OUTPUT FORMAT: Are reporting requirements clear?
4. METRICS: Are specific KPIs or metrics defined?
5. COMPARISON: Are baselines or benchmarks provided?
6. SCOPE: Is the analysis scope well-bounded?

When optimizing prompts:
- Specify data format and structure
- Define the analytical framework
- Clarify output format requirements
- Include relevant metrics/KPIs
- Add context for comparison
- Set clear scope boundaries

Always maintain analytical rigor while making prompts more precise and actionable."""
    
    @property
    def rubric(self) -> dict:
        return {
            "data_context": {"weight": 20, "description": "Data source, format, and structure clarity"},
            "analysis_specification": {"weight": 20, "description": "Type of analysis clearly defined"},
            "output_requirements": {"weight": 15, "description": "Report format and structure"},
            "metrics_definition": {"weight": 15, "description": "KPIs and metrics specified"},
            "scope_boundaries": {"weight": 15, "description": "Analysis scope is well-defined"},
            "actionability": {"weight": 15, "description": "Can be executed with available data"},
        }
