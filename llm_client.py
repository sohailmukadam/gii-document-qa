import subprocess
from typing import Dict, Any, List

class LLMClient:
    """Client for interacting with Ollama local models."""    
    def __init__(self, provider: str = "ollama"):
        """Initialize the LLM client."""
        if provider != "ollama":
            raise ValueError(f"Only 'ollama' provider is supported, got: {provider}")
        self.provider = provider
    
    def ask_question(self, document_text: str, question: str, model: str = "gemma2:2b") -> Dict[str, Any]:
        """Ask a single question about the document."""
        prompt = self.build_prompt(document_text, question)
        answer = self.call_ollama(model, prompt)
        return {
            "answer": self.clean_answer(answer),
            "model": model,
            "provider": self.provider
        }
    
    def ask_questions_batch(self, document_text: str, questions: List[str], model: str = "gemma2:2b") -> List[Dict[str, Any]]:
        """Ask multiple questions sequentially."""
        results = []
        for question in questions:
            try:
                result = self.ask_question(document_text, question, model)
                results.append(result)
            except Exception as e:
                results.append({
                    "answer": None,
                    "model": model,
                    "provider": self.provider,
                    "error": str(e)
                })
        return results
    
    def build_prompt(self, document_text: str, question: str) -> str:
        """Build a concise prompt for CSV-friendly output."""
        return f"Answer this question based on the document below. Be concise and use complete sentences. If listing items, separate with semicolons. No bullet points or markdown. Document: {document_text} Question: {question} Answer:"
    
    def call_ollama(self, model: str, prompt: str) -> str:
        """Call Ollama via subprocess."""
        try:
            result = subprocess.run(
                ["ollama", "run", model, prompt],
                capture_output=True,
                text=True,
                check=True,
                timeout=120
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise Exception(f"Ollama error: {e.stderr}")
        except subprocess.TimeoutExpired:
            raise Exception("Ollama request timed out")
    
    def clean_answer(self, answer: str) -> str:
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
            # Parse model names from output.
            models = []
            for line in result.stdout.split('\n')[1:]:
                if line.strip():
                    model_name = line.split()[0]
                    models.append(model_name)
            return {"ollama": models if models else ["gemma2:2b"]}
        except:
            return {"ollama": ["gemma2:2b"]}