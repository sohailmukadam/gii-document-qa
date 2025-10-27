"""
Simplified and faster LLM Client with concurrent processing support.
"""

import subprocess
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed


class LLMClient:
    """Client for interacting with Ollama local models."""
    
    def __init__(self, provider: str = "ollama", max_workers: int = 4):
        """
        Initialize the LLM client.
        
        Args:
            provider: LLM provider (only 'ollama' supported)
            max_workers: Maximum concurrent requests (default: 4)
        """
        if provider != "ollama":
            raise ValueError(f"Only 'ollama' provider is supported, got: {provider}")
        
        self.provider = provider
        self.max_workers = max_workers
    
    def ask_question(self, document_text: str, question: str, 
                    model: str = "gemma2:2b") -> Dict[str, Any]:
        """
        Ask a single question about the document.
        
        Args:
            document_text: The text content of the document
            question: The question to ask
            model: Model name (default: gemma2:2b)
            
        Returns:
            Dictionary with answer, model, and provider information
        """
        prompt = self._build_prompt(document_text, question)
        answer = self._call_ollama(model, prompt)
        
        return {
            "answer": self._clean_answer(answer),
            "model": model,
            "provider": self.provider
        }
    
    def ask_questions_batch(self, document_text: str, questions: List[str],
                          model: str = "gemma2:2b") -> List[Dict[str, Any]]:
        """
        Ask multiple questions concurrently for speed.
        
        Args:
            document_text: The text content of the document
            questions: List of questions to ask
            model: Model name (default: gemma2:2b)
            
        Returns:
            List of result dictionaries
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all questions at once
            future_to_question = {
                executor.submit(self.ask_question, document_text, q, model): q 
                for q in questions
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_question):
                question = future_to_question[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append({
                        "answer": None,
                        "model": model,
                        "provider": self.provider,
                        "error": str(e)
                    })
        
        return results
    
    def _build_prompt(self, document_text: str, question: str) -> str:
        """Build a concise prompt for CSV-friendly output."""
        return f"""Answer this question based on the document below. Be concise and use complete sentences. If listing items, separate with semicolons. No bullet points or markdown.

Document:
{document_text}

Question: {question}

Answer:"""
    
    def _call_ollama(self, model: str, prompt: str) -> str:
        """Call Ollama via subprocess (synchronous, but fast enough)."""
        try:
            result = subprocess.run(
                ["ollama", "run", model, prompt],
                capture_output=True,
                text=True,
                check=True,
                timeout=120  # 2 minute timeout
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise Exception(f"Ollama error: {e.stderr}")
        except subprocess.TimeoutExpired:
            raise Exception("Ollama request timed out")
    
    def _clean_answer(self, answer: str) -> str:
        """Clean answer for CSV compatibility."""
        if not answer:
            return ""
        
        # Join lines into single paragraph
        lines = [line.strip() for line in answer.split('\n') if line.strip()]
        cleaned = ' '.join(lines)
        
        # Remove extra spaces
        while '  ' in cleaned:
            cleaned = cleaned.replace('  ', ' ')
        
        return cleaned.strip()
    
    def get_available_models(self) -> Dict[str, list]:
        """Get list of available models."""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                check=True
            )
            # Parse model names from output (skip header)
            models = []
            for line in result.stdout.split('\n')[1:]:
                if line.strip():
                    model_name = line.split()[0]
                    models.append(model_name)
            
            return {"ollama": models if models else ["gemma2:2b"]}
        except:
            return {"ollama": ["gemma2:2b"]}