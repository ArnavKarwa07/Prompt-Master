"""
File Ingestion Service
Handles file processing, text extraction, and embedding generation.
Stores only vectors + metadata in DB, raw files in Supabase Storage.
"""
import tiktoken
from typing import AsyncGenerator
from pypdf import PdfReader
from docx import Document
import io

from app.core.config import get_settings
from app.core.supabase_client import get_supabase_service


class FileIngestionService:
    """
    Service for processing uploaded files.
    Implements lean storage strategy - no raw text in DB.
    """
    
    SUPPORTED_EXTENSIONS = {'.txt', '.pdf', '.docx', '.md'}
    
    def __init__(self):
        self.settings = get_settings()
        self.supabase = get_supabase_service()
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
    
    def extract_text(self, file_content: bytes, filename: str) -> str:
        """Extract text content from various file formats."""
        ext = filename.lower().split('.')[-1]
        
        if ext == 'txt' or ext == 'md':
            return file_content.decode('utf-8', errors='ignore')
        
        elif ext == 'pdf':
            return self._extract_pdf(file_content)
        
        elif ext == 'docx':
            return self._extract_docx(file_content)
        
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    
    def _extract_pdf(self, content: bytes) -> str:
        """Extract text from PDF."""
        reader = PdfReader(io.BytesIO(content))
        text_parts = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        return "\n\n".join(text_parts)
    
    def _extract_docx(self, content: bytes) -> str:
        """Extract text from DOCX."""
        doc = Document(io.BytesIO(content))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n\n".join(paragraphs)
    
    def chunk_text(
        self, 
        text: str, 
        max_tokens: int = None,
        overlap_tokens: int = None
    ) -> list[str]:
        """
        Split text into chunks for embedding.
        Uses token-based splitting for accuracy.
        """
        max_tokens = max_tokens or self.settings.max_chunk_size
        overlap_tokens = overlap_tokens or self.settings.chunk_overlap
        
        tokens = self.tokenizer.encode(text)
        chunks = []
        
        start = 0
        while start < len(tokens):
            end = min(start + max_tokens, len(tokens))
            chunk_tokens = tokens[start:end]
            chunk_text = self.tokenizer.decode(chunk_tokens)
            chunks.append(chunk_text)
            start = end - overlap_tokens
            
            # Prevent infinite loop
            if start >= len(tokens) - overlap_tokens:
                break
        
        return chunks
    
    def generate_summary(self, chunk: str, max_length: int = 255) -> str:
        """
        Generate a short summary of a chunk.
        For lean storage - we store summaries, not full text.
        """
        # Simple extractive summary: first N characters
        # In production, could use LLM for better summaries
        summary = chunk.strip()[:max_length]
        if len(chunk) > max_length:
            # Try to end at a word boundary
            last_space = summary.rfind(' ')
            if last_space > max_length * 0.7:
                summary = summary[:last_space] + "..."
            else:
                summary = summary + "..."
        return summary
    
    async def process_file(
        self,
        file_content: bytes,
        filename: str,
        user_id: str,
        project_id: str
    ) -> dict:
        """
        Full file processing pipeline:
        1. Upload to Supabase Storage
        2. Extract text
        3. Chunk text
        4. Generate embeddings (TODO: integrate with embedding model)
        5. Store vectors with summaries (not full text)
        
        Returns processing results.
        """
        # 1. Upload to storage
        storage_path = await self.supabase.upload_file(
            file_path=f"{project_id}/{filename}",
            file_content=file_content,
            user_id=user_id
        )
        
        # 2. Extract text
        text = self.extract_text(file_content, filename)
        
        # 3. Chunk text
        chunks = self.chunk_text(text)
        
        # 4. Generate summaries (for lean storage)
        summaries = [self.generate_summary(chunk) for chunk in chunks]
        
        # 5. Prepare metadata
        metadata_list = [
            {
                "project_id": project_id,
                "user_id": user_id,
                "filename": filename,
                "storage_path": storage_path,
                "chunk_index": i,
                "total_chunks": len(chunks)
            }
            for i in range(len(chunks))
        ]
        
        # TODO: Generate actual embeddings using embedding model
        # For now, return processing summary
        # embeddings = await self._generate_embeddings(chunks)
        # await self.supabase.store_vectors(embeddings, summaries, metadata_list)
        
        return {
            "storage_path": storage_path,
            "filename": filename,
            "chunks_created": len(chunks),
            "status": "processed",
            "message": "File uploaded and chunked. Embedding generation pending."
        }


def get_ingestion_service() -> FileIngestionService:
    """Dependency injection for ingestion service."""
    return FileIngestionService()
