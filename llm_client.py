"""
LLM Client module with improved prompting for CSV-friendly outputs.
"""

import asyncio
from typing import Optional, Dict, Any


class LLMClient:
    """Client for interacting with Ollama local models."""
    
    def __init__(self, provider: str = "ollama"):
        """
        Initialize the LLM client.
        
        Args:
            provider: LLM provider (kept for compatibility, only 'ollama' supported)
        """
        self.provider = provider
        if provider != "ollama":
            raise ValueError(f"Only 'ollama' provider is supported, got: {provider}")
    
    def ask_question(self, document_text: str, question: str, 
                    model: Optional[str] = None) -> Dict[str, Any]:
        """
        Ask a question about the document (synchronous wrapper).
        
        Args:
            document_text: The text content of the document
            question: The question to ask
            model: Optional model name (defaults to gemma2:2b)
            
        Returns:
            Dictionary with answer, model, and provider information
        """
        return asyncio.run(self._ask_question_async(document_text, question, model))
    
    def ask_question_structured(self, document_text: str, question: str, 
                               model: Optional[str] = None) -> Dict[str, Any]:
        """
        Ask a question with structured prompting for CSV-friendly output.
        
        Args:
            document_text: The text content of the document
            question: The question to ask
            model: Optional model name (defaults to gemma2:2b)
            
        Returns:
            Dictionary with answer, model, and provider information
        """
        return asyncio.run(self._ask_question_structured_async(document_text, question, model))
    
    async def _ask_question_async(self, document_text: str, question: str, 
                                  model: Optional[str] = None) -> Dict[str, Any]:
        """
        Async implementation of ask_question (standard prompting).
        """
        if not model:
            model = "gemma2:2b"
        
        prompt = f"""You are a helpful assistant that answers questions based on the provided document content.

Document Content:
{document_text}

Question: {question}

Please provide a comprehensive answer based on the document content. If the answer cannot be found in the document, please state that clearly.
"""
        
        try:
            process = await asyncio.create_subprocess_exec(
                "ollama", "run", model, prompt,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"Ollama command failed: {stderr.decode().strip()}")
            
            answer = stdout.decode().strip()
            
            return {
                "answer": answer,
                "model": model,
                "provider": self.provider
            }
        
        except Exception as e:
            raise Exception(f"Ollama error: {str(e)}")
    
    async def _ask_question_structured_async(self, document_text: str, question: str, 
                                            model: Optional[str] = None) -> Dict[str, Any]:
        """
        Async implementation with structured prompting for CSV-friendly output.
        """
        if not model:
            model = "gemma2:2b"
        
        prompt = f"""You are a helpful assistant that answers questions based on the provided document content.

Document Content:
{document_text}

Question: {question}

Please provide a clear, concise answer based on the document content. Format your response as follows:
- Use complete sentences but be concise
- Write in a single paragraph without line breaks
- If listing multiple items, separate them with semicolons (;) not bullet points
- Keep the answer focused and to-the-point
- If the answer cannot be found in the document, state "Information not found in document"
- Do not use markdown formatting, bullet points, or numbered lists

Answer:"""
        
        try:
            process = await asyncio.create_subprocess_exec(
                "ollama", "run", model, prompt,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"Ollama command failed: {stderr.decode().strip()}")
            
            answer = stdout.decode().strip()
            
            return {
                "answer": answer,
                "model": model,
                "provider": self.provider
            }
        
        except Exception as e:
            raise Exception(f"Ollama error: {str(e)}")
    
    def get_available_models(self) -> Dict[str, list]:
        """
        Get list of available models.
        
        Returns:
            Dictionary with provider as key and list of models as value
        """
        return {
            "ollama": ["gemma2:2b"]
        }


# Test the module
async def test_client():
    """Test function for the LLM client."""
    client = LLMClient()
    
    # Read the processed document
    with open("documents_read/ghana_gonja_marriage.txt", 'r', encoding='utf-8') as f:
        document_text = f.read()
    
    # Ask a question with structured prompting
    result = await client._ask_question_structured_async(
        document_text=document_text,
        question="What is this document about?",
        model="gemma2:2b"
    )
    
    print(f"Model: {result['model']}")
    print(f"Provider: {result['provider']}")
    print(f"\nAnswer:\n{result['answer']}")


if __name__ == "__main__":
    asyncio.run(test_client())