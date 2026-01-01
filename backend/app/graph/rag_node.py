"""
RAG Node Module
Handles retrieval-augmented generation for prompt engineering context.
Uses a local knowledge base with semantic chunking and keyword-based retrieval.
"""
from langchain_groq import ChatGroq
from app.core.config import get_settings
from app.core.supabase_client import get_supabase_service
from typing import Optional, List, Dict
from pathlib import Path
import re
import os
import logging

logger = logging.getLogger(__name__)


class KnowledgeChunk:
    """Represents a chunk of knowledge from the knowledge base."""
    def __init__(self, section: str, topic: str, content: str, keywords: List[str]):
        self.section = section
        self.topic = topic
        self.content = content
        self.keywords = keywords
    
    def to_dict(self) -> dict:
        return {
            "section": self.section,
            "topic": self.topic,
            "content": self.content,
            "keywords": self.keywords
        }


class PromptEngineeringKnowledgeBase:
    """
    Knowledge base for prompt engineering best practices.
    Loads from markdown file and provides semantic search.
    """
    
    def __init__(self):
        self.chunks: List[KnowledgeChunk] = []
        self._load_knowledge_base()
    
    def _get_kb_path(self) -> Path:
        """Get the path to the knowledge base file."""
        # Try multiple possible locations
        possible_paths = [
            Path(__file__).parent.parent.parent / "knowledge_base" / "prompt_engineering_kb.md",
            Path("knowledge_base/prompt_engineering_kb.md"),
            Path("backend/knowledge_base/prompt_engineering_kb.md"),
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        
        # Fallback: create knowledge base directory if needed
        kb_dir = Path(__file__).parent.parent.parent / "knowledge_base"
        kb_dir.mkdir(exist_ok=True)
        return kb_dir / "prompt_engineering_kb.md"
    
    def _load_knowledge_base(self):
        """Load and parse the knowledge base markdown file."""
        kb_path = self._get_kb_path()
        
        if not kb_path.exists():
            logger.debug(f"Knowledge base not found at {kb_path}, using defaults")
            self._load_default_knowledge()
            return
        
        try:
            with open(kb_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self._parse_markdown(content)
            logger.debug(f"Loaded {len(self.chunks)} knowledge chunks")
        except Exception as e:
            logger.warning(f"Error loading knowledge base: {e}, using defaults")
            self._load_default_knowledge()
    
    def _parse_markdown(self, content: str):
        """Parse markdown content into searchable chunks."""
        current_section = "GENERAL"
        current_topic = ""
        current_content = []
        
        lines = content.split('\n')
        
        for line in lines:
            # Check for section markers
            section_match = re.match(r'^## SECTION:\s*(.+)$', line)
            if section_match:
                # Save previous chunk if exists
                if current_content and current_topic:
                    self._add_chunk(current_section, current_topic, '\n'.join(current_content))
                current_section = section_match.group(1).strip()
                current_topic = ""
                current_content = []
                continue
            
            # Check for topic markers (### headers)
            topic_match = re.match(r'^###\s+(?:Topic|Technique|Template|Strategy|Metric|Anti-Pattern|Agent Type|Temperature|Defense|Attack Pattern):\s*(.+)$', line)
            if topic_match:
                # Save previous chunk if exists
                if current_content and current_topic:
                    self._add_chunk(current_section, current_topic, '\n'.join(current_content))
                current_topic = topic_match.group(1).strip()
                current_content = []
                continue
            
            # Accumulate content
            if current_topic and line.strip():
                current_content.append(line)
        
        # Don't forget the last chunk
        if current_content and current_topic:
            self._add_chunk(current_section, current_topic, '\n'.join(current_content))
    
    def _add_chunk(self, section: str, topic: str, content: str):
        """Add a chunk with extracted keywords."""
        keywords = self._extract_keywords(section, topic, content)
        chunk = KnowledgeChunk(section, topic, content, keywords)
        self.chunks.append(chunk)
    
    def _extract_keywords(self, section: str, topic: str, content: str) -> List[str]:
        """Extract searchable keywords from content."""
        keywords = []
        
        # Add section and topic as keywords
        keywords.extend(section.lower().replace('_', ' ').split())
        keywords.extend(topic.lower().split())
        
        # Extract key terms from content
        content_lower = content.lower()
        
        # Technique-related keywords
        technique_keywords = [
            'zero-shot', 'one-shot', 'few-shot', 'chain-of-thought', 'cot',
            'react', 'tree of thoughts', 'tot', 'rag', 'retrieval',
            'meta-prompt', 'recursive', 'chaining', 'persona', 'role',
            'constitutional', 'self-refinement', 'least-to-most'
        ]
        
        # Quality-related keywords
        quality_keywords = [
            'clarity', 'specificity', 'context', 'format', 'structure',
            'ambiguity', 'constraint', 'example', 'output', 'input'
        ]
        
        # Task-related keywords
        task_keywords = [
            'code', 'coding', 'debug', 'review', 'test', 'refactor',
            'creative', 'writing', 'story', 'analysis', 'summarize',
            'translate', 'classify', 'extract', 'generate'
        ]
        
        # Agent-related keywords
        agent_keywords = [
            'agent', 'temperature', 'system prompt', 'user prompt',
            'hallucination', 'security', 'injection'
        ]
        
        all_keywords = technique_keywords + quality_keywords + task_keywords + agent_keywords
        
        for kw in all_keywords:
            if kw in content_lower:
                keywords.append(kw)
        
        return list(set(keywords))
    
    def _load_default_knowledge(self):
        """Load default knowledge if file not available."""
        default_chunks = [
            ("CORE_TECHNIQUES", "Zero-Shot Prompting", 
             "Presenting a task without examples. Best for straightforward tasks. Token-efficient but may have format variance."),
            ("CORE_TECHNIQUES", "Few-Shot Prompting",
             "Providing 3-5 examples for in-context learning. Gold standard for reliability without fine-tuning."),
            ("CORE_TECHNIQUES", "Chain-of-Thought",
             "Encourage intermediate reasoning steps. Essential for math, logic, debugging. Use 'Let's think step by step'."),
            ("QUALITY_METRICS", "Clarity",
             "Use imperative sentences. Avoid conditional clauses. Be unambiguous."),
            ("QUALITY_METRICS", "Specificity",
             "Define constraints: length, format, style. Use type constraints (JSON, SQL). State what NOT to do."),
            ("ANTI_PATTERNS", "Negative Constraint Trap",
             "LLMs struggle with negation. Instead of 'Don't write long sentences', use 'Write short sentences'."),
            ("ANTI_PATTERNS", "Mind Reader Assumption",
             "Avoid vague terms like 'better'. Be specific: 'more concise and professional'."),
            ("BEST_PRACTICES", "Checklist",
             "1. Clear role 2. Specific task verb 3. Context provided 4. Constraints defined 5. Format specified 6. Examples included 7. Delimiters used 8. CoT for complex tasks"),
        ]
        
        for section, topic, content in default_chunks:
            keywords = self._extract_keywords(section, topic, content)
            self.chunks.append(KnowledgeChunk(section, topic, content, keywords))
    
    def search(self, query: str, goal: str = "", top_k: int = 5) -> List[KnowledgeChunk]:
        """
        Search the knowledge base for relevant chunks.
        Uses keyword matching with scoring.
        """
        query_lower = (query + " " + goal).lower()
        query_words = set(query_lower.split())
        
        scored_chunks = []
        
        for chunk in self.chunks:
            score = 0
            
            # Score based on keyword matches
            for keyword in chunk.keywords:
                if keyword in query_lower:
                    score += 2
                # Partial word matching
                for word in query_words:
                    if word in keyword or keyword in word:
                        score += 1
            
            # Boost for section relevance
            section_lower = chunk.section.lower().replace('_', ' ')
            for word in query_words:
                if word in section_lower:
                    score += 1
            
            # Boost for topic relevance
            topic_lower = chunk.topic.lower()
            for word in query_words:
                if word in topic_lower:
                    score += 2
            
            # Content word matching
            content_lower = chunk.content.lower()
            matching_words = sum(1 for word in query_words if word in content_lower and len(word) > 3)
            score += matching_words * 0.5
            
            if score > 0:
                scored_chunks.append((score, chunk))
        
        # Sort by score descending
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        
        return [chunk for _, chunk in scored_chunks[:top_k]]


class RAGNode:
    """
    RAG Node for fetching prompt engineering documentation.
    All agents can query this node for additional context.
    """
    
    def __init__(self):
        settings = get_settings()
        self.llm = ChatGroq(
            api_key=settings.groq_api_key,
            model_name=settings.secondary_model,
            temperature=0,
        )
        self.supabase = get_supabase_service()
        self.knowledge_base = PromptEngineeringKnowledgeBase()
    
    async def get_relevant_context(
        self, 
        prompt: str, 
        goal: str,
        agent_type: str = "general",
        use_database: bool = False
    ) -> str:
        """
        Get relevant prompt engineering context.
        
        Args:
            prompt: The user's prompt to analyze
            goal: The user's stated goal
            agent_type: Type of agent (coding, creative, analyst, general)
            use_database: Whether to use vector search (for authenticated users)
        
        Returns:
            Relevant context as a string
        """
        # Search knowledge base
        relevant_chunks = self.knowledge_base.search(prompt, goal, top_k=7)
        
        # Also search for agent-specific tips
        agent_chunks = self.knowledge_base.search(agent_type, "", top_k=2)
        
        # Combine and deduplicate
        all_chunks = relevant_chunks + [c for c in agent_chunks if c not in relevant_chunks]
        
        if not all_chunks:
            return self._get_fallback_context()
        
        # Build context string
        context = "PROMPT ENGINEERING KNOWLEDGE BASE:\n\n"
        
        for chunk in all_chunks[:8]:  # Limit to 8 chunks to avoid context overflow
            context += f"## {chunk.section} - {chunk.topic}\n"
            context += f"{chunk.content}\n\n"
        
        return context
    
    def _get_fallback_context(self) -> str:
        """Provide fallback context if no relevant chunks found."""
        return """PROMPT ENGINEERING BEST PRACTICES:

• CLARITY: Use imperative sentences. Be unambiguous. Avoid conditional clauses.

• SPECIFICITY: Define constraints clearly - length, format, style. Specify output format (JSON, Markdown).

• CONTEXT: Provide necessary background. Define the role ("You are an expert...").

• EXAMPLES: Include 2-3 examples for complex tasks (few-shot prompting).

• STRUCTURE: Use bullet points, numbered lists, or XML tags for complex prompts.

• CHAIN-OF-THOUGHT: For reasoning tasks, add "Let's think step by step".

• AVOID NEGATION: Instead of "Don't do X", say "Do Y instead".

• FORMAT OUTPUT: Explicitly define expected output structure.
"""
    
    async def get_technique_info(self, technique_name: str) -> str:
        """Get detailed information about a specific prompting technique."""
        chunks = self.knowledge_base.search(technique_name, "", top_k=3)
        
        if not chunks:
            return f"No specific information found for technique: {technique_name}"
        
        result = f"Information about {technique_name}:\n\n"
        for chunk in chunks:
            result += f"{chunk.content}\n\n"
        
        return result
    
    async def get_agent_optimization_tips(self, agent_type: str) -> str:
        """Get optimization tips for a specific agent type."""
        # Search for agent-specific content
        queries = [agent_type, f"{agent_type} agent", f"{agent_type} optimization"]
        
        all_chunks = []
        for query in queries:
            chunks = self.knowledge_base.search(query, "", top_k=2)
            all_chunks.extend([c for c in chunks if c not in all_chunks])
        
        if not all_chunks:
            return self._get_default_agent_tips(agent_type)
        
        result = f"Optimization tips for {agent_type} agents:\n\n"
        for chunk in all_chunks[:4]:
            result += f"### {chunk.topic}\n{chunk.content}\n\n"
        
        return result
    
    def _get_default_agent_tips(self, agent_type: str) -> str:
        """Default tips by agent type."""
        tips = {
            "coding": """Coding Agent Tips:
• Use low temperature (0.0-0.2) for deterministic output
• Enable Chain-of-Thought for debugging
• Provide file context and library definitions
• Specify language and framework explicitly
• Request code-only output without explanations""",
            
            "creative": """Creative Agent Tips:
• Use higher temperature (0.7-1.0) for varied output
• Provide style references and persona
• Include world-building context
• Avoid clichés explicitly
• Focus on sensory details and emotional resonance""",
            
            "analyst": """Analyst Agent Tips:
• Use medium temperature (0.2-0.4)
• Require step-by-step reasoning
• Demand citations for claims
• Provide data schemas and context
• Handle missing data gracefully""",
            
            "general": """General Agent Tips:
• Use balanced temperature (0.5)
• Include intent classification
• Provide clear task verbs
• Define output format explicitly
• Use examples when possible"""
        }
        
        return tips.get(agent_type, tips["general"])
    
    async def search_knowledge_base(
        self,
        query: str,
        match_count: int = 5
    ) -> List[dict]:
        """
        Search the knowledge base for relevant documents.
        
        Args:
            query: Search query
            match_count: Number of results to return
        
        Returns:
            List of matching documents with content and metadata
        """
        chunks = self.knowledge_base.search(query, "", top_k=match_count)
        return [chunk.to_dict() for chunk in chunks]
    
    def get_all_techniques(self) -> List[str]:
        """Get a list of all available prompting techniques."""
        techniques = []
        for chunk in self.knowledge_base.chunks:
            if "TECHNIQUE" in chunk.section or "Technique:" in chunk.topic:
                techniques.append(chunk.topic)
        return list(set(techniques))
    
    def get_anti_patterns(self) -> List[dict]:
        """Get all anti-patterns to avoid."""
        anti_patterns = []
        for chunk in self.knowledge_base.chunks:
            if "ANTI_PATTERN" in chunk.section:
                anti_patterns.append({
                    "name": chunk.topic,
                    "description": chunk.content
                })
        return anti_patterns


# Singleton
_rag_node = None


def get_rag_node() -> RAGNode:
    """Get or create the RAG node singleton."""
    global _rag_node
    if _rag_node is None:
        _rag_node = RAGNode()
    return _rag_node
