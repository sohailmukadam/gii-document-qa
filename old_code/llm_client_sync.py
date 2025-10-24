"""
Synchronous LLM client module for interacting with various language models.
"""

import os
from typing import Optional, Dict, Any
from openai import OpenAI
import anthropic
from dotenv import load_dotenv

load_dotenv()


class LLMClientSync:
    """Synchronous client for interacting with various LLM providers."""
    
    def __init__(self, provider: str = "openai"):
        self.provider = provider.lower()
        self.openai_client = None
        self.anthropic_client = None
        
        if self.provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required")
            self.openai_client = OpenAI(api_key=api_key)
        
        elif self.provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable is required")
            self.anthropic_client = anthropic.Anthropic(api_key=api_key)
        
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def ask_question(self, document_text: str, question: str, 
                    model: Optional[str] = None) -> Dict[str, Any]:
        """
        Ask a question about the document content.
        
        Args:
            document_text: The text content of the document
            question: The question to ask about the document
            model: Specific model to use (optional)
            
        Returns:
            Dictionary containing the answer and metadata
        """
        if self.provider == "openai":
            return self._ask_openai(document_text, question, model)
        elif self.provider == "anthropic":
            return self._ask_anthropic(document_text, question, model)
    
    def _ask_openai(self, document_text: str, question: str, 
                   model: Optional[str] = None) -> Dict[str, Any]:
        """Ask question using OpenAI API."""
        if not model:
            model = "gpt-3.5-turbo"
        
        prompt = f"""You are a helpful assistant that answers questions based on the provided document content.

Document Content:
{document_text}

Question: {question}

Please provide a comprehensive answer based on the document content. If the answer cannot be found in the document, please state that clearly."""

        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on document content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            return {
                "answer": response.choices[0].message.content,
                "provider": "openai",
                "model": model,
                "usage": response.usage.dict() if response.usage else None
            }
        
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def _ask_anthropic(self, document_text: str, question: str, 
                     model: Optional[str] = None) -> Dict[str, Any]:
        """Ask question using Anthropic API."""
        if not model:
            model = "claude-3-sonnet-20240229"
        
        prompt = f"""You are a helpful assistant that answers questions based on the provided document content.

Document Content:
{document_text}

Question: {question}

Please provide a comprehensive answer based on the document content. If the answer cannot be found in the document, please state that clearly."""

        try:
            response = self.anthropic_client.messages.create(
                model=model,
                max_tokens=1000,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return {
                "answer": response.content[0].text,
                "provider": "anthropic",
                "model": model,
                "usage": response.usage.dict() if response.usage else None
            }
        
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")
    
    def get_available_models(self) -> Dict[str, list]:
        """Get available models for each provider."""
        return {
            "openai": [
                "gpt-3.5-turbo",
                "gpt-4",
                "gpt-4-turbo-preview"
            ],
            "anthropic": [
                "claude-3-haiku-20240307",
                "claude-3-sonnet-20240229",
                "claude-3-opus-20240229"
            ]
        }