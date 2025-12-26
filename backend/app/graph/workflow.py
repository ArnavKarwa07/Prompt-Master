"""
LangGraph Workflow
Defines the multi-agent graph with supervisor routing.
"""
from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional, Literal, Annotated
from operator import add

from app.agents import get_agent, AgentState, AGENT_REGISTRY
from app.graph.supervisor import get_supervisor
from app.graph.rag_node import get_rag_node


class GraphState(TypedDict):
    """State that flows through the graph."""
    # Input
    prompt: str
    goal: str
    force_agent: Optional[str]
    use_rag: bool
    user_id: Optional[str]
    project_id: Optional[str]
    
    # Routing
    selected_agent: Optional[str]
    routing_confidence: Optional[float]
    routing_reasoning: Optional[str]
    
    # RAG
    rag_context: Optional[str]
    
    # Output
    score: Optional[int]
    feedback: Optional[str]
    optimized_prompt: Optional[str]
    error: Optional[str]


async def supervisor_node(state: GraphState) -> GraphState:
    """
    Supervisor node that routes to the appropriate agent.
    Respects force_agent if provided.
    """
    # If agent is forced by user, use that
    if state.get("force_agent") and state["force_agent"] in AGENT_REGISTRY:
        return {
            **state,
            "selected_agent": state["force_agent"],
            "routing_confidence": 1.0,
            "routing_reasoning": "Agent manually selected by user"
        }
    
    # Otherwise, use supervisor to classify
    supervisor = get_supervisor()
    result = await supervisor.classify(state["prompt"], state["goal"])
    
    return {
        **state,
        "selected_agent": result["agent"],
        "routing_confidence": result["confidence"],
        "routing_reasoning": result["reasoning"]
    }


async def rag_node(state: GraphState) -> GraphState:
    """
    RAG node that fetches relevant prompt engineering context.
    """
    if not state.get("use_rag", True):
        return state
    
    rag = get_rag_node()
    context = await rag.get_relevant_context(
        state["prompt"],
        state["goal"],
        use_database=state.get("user_id") is not None
    )
    
    return {
        **state,
        "rag_context": context
    }


async def coding_agent_node(state: GraphState) -> GraphState:
    """Coding agent evaluation node."""
    agent = get_agent("coding")
    agent_state = {
        "prompt": state["prompt"],
        "goal": state["goal"],
        "context": None,
        "agent_type": None,
        "score": None,
        "feedback": None,
        "optimized_prompt": None,
        "rag_context": state.get("rag_context"),
        "error": None
    }
    result = await agent.evaluate(agent_state)
    
    return {
        **state,
        "score": result.get("score"),
        "feedback": result.get("feedback"),
        "optimized_prompt": result.get("optimized_prompt"),
        "error": result.get("error")
    }


async def creative_agent_node(state: GraphState) -> GraphState:
    """Creative agent evaluation node."""
    agent = get_agent("creative")
    agent_state = {
        "prompt": state["prompt"],
        "goal": state["goal"],
        "context": None,
        "agent_type": None,
        "score": None,
        "feedback": None,
        "optimized_prompt": None,
        "rag_context": state.get("rag_context"),
        "error": None
    }
    result = await agent.evaluate(agent_state)
    
    return {
        **state,
        "score": result.get("score"),
        "feedback": result.get("feedback"),
        "optimized_prompt": result.get("optimized_prompt"),
        "error": result.get("error")
    }


async def analyst_agent_node(state: GraphState) -> GraphState:
    """Analyst agent evaluation node."""
    agent = get_agent("analyst")
    agent_state = {
        "prompt": state["prompt"],
        "goal": state["goal"],
        "context": None,
        "agent_type": None,
        "score": None,
        "feedback": None,
        "optimized_prompt": None,
        "rag_context": state.get("rag_context"),
        "error": None
    }
    result = await agent.evaluate(agent_state)
    
    return {
        **state,
        "score": result.get("score"),
        "feedback": result.get("feedback"),
        "optimized_prompt": result.get("optimized_prompt"),
        "error": result.get("error")
    }


async def general_agent_node(state: GraphState) -> GraphState:
    """General agent evaluation node."""
    agent = get_agent("general")
    agent_state = {
        "prompt": state["prompt"],
        "goal": state["goal"],
        "context": None,
        "agent_type": None,
        "score": None,
        "feedback": None,
        "optimized_prompt": None,
        "rag_context": state.get("rag_context"),
        "error": None
    }
    result = await agent.evaluate(agent_state)
    
    return {
        **state,
        "score": result.get("score"),
        "feedback": result.get("feedback"),
        "optimized_prompt": result.get("optimized_prompt"),
        "error": result.get("error")
    }


def route_to_agent(state: GraphState) -> str:
    """Router function that directs to the selected agent."""
    agent = state.get("selected_agent", "general")
    return f"{agent}_agent"


def build_graph() -> StateGraph:
    """
    Build and return the LangGraph workflow.
    
    Graph structure:
    Entry -> Supervisor -> RAG -> [Agent Selection] -> End
    """
    # Create the graph
    workflow = StateGraph(GraphState)
    
    # Add nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("rag", rag_node)
    workflow.add_node("coding_agent", coding_agent_node)
    workflow.add_node("creative_agent", creative_agent_node)
    workflow.add_node("analyst_agent", analyst_agent_node)
    workflow.add_node("general_agent", general_agent_node)
    
    # Set entry point
    workflow.set_entry_point("supervisor")
    
    # Supervisor -> RAG
    workflow.add_edge("supervisor", "rag")
    
    # RAG -> Conditional routing to agents
    workflow.add_conditional_edges(
        "rag",
        route_to_agent,
        {
            "coding_agent": "coding_agent",
            "creative_agent": "creative_agent",
            "analyst_agent": "analyst_agent",
            "general_agent": "general_agent",
        }
    )
    
    # All agents -> END
    workflow.add_edge("coding_agent", END)
    workflow.add_edge("creative_agent", END)
    workflow.add_edge("analyst_agent", END)
    workflow.add_edge("general_agent", END)
    
    return workflow


# Compiled graph singleton
_compiled_graph = None


def get_graph():
    """Get or create the compiled graph."""
    global _compiled_graph
    if _compiled_graph is None:
        workflow = build_graph()
        _compiled_graph = workflow.compile()
    return _compiled_graph


async def run_prompt_optimization(
    prompt: str,
    goal: str,
    force_agent: Optional[str] = None,
    use_rag: bool = True,
    user_id: Optional[str] = None,
    project_id: Optional[str] = None
) -> dict:
    """
    Run the full prompt optimization workflow.
    
    Args:
        prompt: The prompt to optimize
        goal: The user's stated goal
        force_agent: Optional agent to force (bypass supervisor)
        use_rag: Whether to use RAG for context
        user_id: Optional user ID for authenticated requests
        project_id: Optional project ID for saving history
    
    Returns:
        Complete result with score, feedback, and optimized prompt
    """
    graph = get_graph()
    
    initial_state: GraphState = {
        "prompt": prompt,
        "goal": goal,
        "force_agent": force_agent,
        "use_rag": use_rag,
        "user_id": user_id,
        "project_id": project_id,
        "selected_agent": None,
        "routing_confidence": None,
        "routing_reasoning": None,
        "rag_context": None,
        "score": None,
        "feedback": None,
        "optimized_prompt": None,
        "error": None,
    }
    
    result = await graph.ainvoke(initial_state)
    
    return {
        "prompt": result["prompt"],
        "goal": result["goal"],
        "agent": result["selected_agent"],
        "routing": {
            "confidence": result["routing_confidence"],
            "reasoning": result["routing_reasoning"]
        },
        "score": result["score"],
        "feedback": result["feedback"],
        "optimized_prompt": result["optimized_prompt"],
        "error": result.get("error")
    }
