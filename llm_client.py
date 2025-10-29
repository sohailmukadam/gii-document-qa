import google.generativeai as genai
from typing import Dict, Any, List
import os
from dotenv import load_dotenv

class LLMClient:
    """Client for interacting with Google Gemini models."""    
    def __init__(self, provider: str = "gemini", api_key: str = None):
        """Initialize the LLM client."""
        if provider != "gemini":
            raise ValueError(f"Only 'gemini' provider is supported, got: {provider}")
        self.provider = provider
        
        # Configure Gemini
        load_dotenv()
        api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("API key required. Set GEMINI_API_KEY environment variable or pass api_key parameter")
        genai.configure(api_key=api_key)
    
    def ask_question(self, document_text: str, question: str, model: str = "gemini-2.0-flash-lite") -> Dict[str, Any]:
        """Ask a single question about the document."""
        prompt = self.build_prompt(document_text, question)
        answer = self.call_gemini(model, prompt)
        return {
            "answer": self.clean_answer(answer),
            "model": model,
            "provider": self.provider
        }
    
    def ask_questions_batch(self, document_text: str, questions: List[str], model: str = "gemini-2.0-flash-lite") -> List[Dict[str, Any]]:
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
    
    def call_gemini(self, model: str, prompt: str) -> str:
        """Call Gemini API."""
        try:
            # Create the model
            gemini_model = genai.GenerativeModel(model)
            
            # Generate response
            response = gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=500,
                )
            )
            
            return response.text.strip()
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
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
        """Get list of available Gemini models."""
        return {
            "gemini": [
                "gemini-2.0-flash-lite"
            ]
        }