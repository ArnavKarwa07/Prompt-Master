"""
RAG Node Module
Handles retrieval-augmented generation for prompt engineering context.
"""
from langchain_groq import ChatGroq
from app.core.config import get_settings
from app.core.supabase_client import get_supabase_service
from typing import Optional
import numpy as np


class RAGNode:
    """
    RAG Node for fetching prompt engineering documentation.
    All agents can query this node for additional context.
    """
    
    # Prompt engineering knowledge base (embedded on first use)
    PROMPT_ENGINEERING_TIPS = [
        {
            "topic": "clarity",
            "content": "Clear prompts specify exactly what you want. Avoid ambiguity by using precise language and defining terms that could be interpreted multiple ways."
        },
        {
            "topic": "context",
            "content": "Provide relevant background information. Tell the AI what role it should play, what the situation is, and any constraints or requirements."
        },
        {
            "topic": "examples",
            "content": "Few-shot prompting: Include 2-3 examples of the desired input-output format to guide the model's responses."
        },
        {
            "topic": "structure",
            "content": "Use structured formatting like bullet points, numbered lists, or XML tags to organize complex prompts and expected outputs."
        },
        {
            "topic": "constraints",
            "content": "Specify constraints clearly: length limits, format requirements, topics to avoid, or specific points to include."
        },
        {
            "topic": "chain_of_thought",
            "content": "For reasoning tasks, ask the model to 'think step by step' or 'explain your reasoning' to improve accuracy."
        },
        {
            "topic": "role_prompting",
            "content": "Assign a specific role or persona: 'You are an expert Python developer' helps focus responses on domain expertise."
        },
        {
            "topic": "output_format",
            "content": "Specify the exact output format you want: JSON, markdown, bullet points, or a specific template structure."
        },
        {
            "topic": "iteration",
            "content": "Break complex tasks into subtasks. Use multi-turn conversations to refine and build on previous outputs."
        },
        {
            "topic": "negative_prompts",
            "content": "Specify what NOT to do: 'Do not include disclaimers' or 'Avoid technical jargon' can improve output quality."
        },
    ]
    
    def __init__(self):
        settings = get_settings()
        self.llm = ChatGroq(
            api_key=settings.groq_api_key,
            model_name=settings.secondary_model,
            temperature=0,
        )
        self.supabase = get_supabase_service()
    
    async def get_relevant_context(
        self, 
        prompt: str, 
        goal: str,
        use_database: bool = False
    ) -> str:
        """
        Get relevant prompt engineering context.
        
        Args:
            prompt: The user's prompt to analyze
            goal: The user's stated goal
            use_database: Whether to use vector search (for authenticated users)
        
        Returns:
            Relevant context as a string
        """
        # For now, use the built-in knowledge base
        # In production, this would do vector similarity search
        relevant_tips = self._get_relevant_tips(prompt, goal)
        
        if use_database:
            # TODO: Add vector search from Supabase
            pass
        
        context = "PROMPT ENGINEERING BEST PRACTICES:\n\n"
        for tip in relevant_tips:
            context += f"• {tip['topic'].upper()}: {tip['content']}\n\n"
        
        return context
    
    def _get_relevant_tips(self, prompt: str, goal: str, top_k: int = 5) -> list:
        """
        Get the most relevant tips based on keyword matching.
        In production, this would use embeddings for semantic search.
        """
        prompt_lower = (prompt + " " + goal).lower()
        
        scored_tips = []
        for tip in self.PROMPT_ENGINEERING_TIPS:
            score = 0
            # Simple keyword matching
            keywords = tip['topic'].split('_') + tip['content'].lower().split()
            for keyword in keywords:
                if keyword in prompt_lower:
                    score += 1
            scored_tips.append((score, tip))
        
        # Sort by score and return top_k
        scored_tips.sort(reverse=True, key=lambda x: x[0])
        return [tip for _, tip in scored_tips[:top_k]]
    
    async def search_knowledge_base(
        self,
        query: str,
        match_count: int = 5
    ) -> list[dict]:
        """
        Search the vector knowledge base for relevant documents.
        
        Args:
            query: Search query
            match_count: Number of results to return
        
        Returns:
            List of matching documents with summaries and metadata
        """
        # This would use embedding + vector search in production
        # For now, return the built-in tips
        return self.PROMPT_ENGINEERING_TIPS[:match_count]


# Singleton
_rag_node = None


def get_rag_node() -> RAGNode:
    """Get or create the RAG node singleton."""
    global _rag_node
    if _rag_node is None:
        _rag_node = RAGNode()
    return _rag_node
