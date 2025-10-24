"""
Batch Q&A processing module with improved LLM output formatting for CSV.
"""

import csv
import os
from typing import List, Dict, Any
from datetime import datetime
from llm_client import LLMClient


class BatchQAProcessor:
    """Handles batch question processing with CSV-optimized outputs."""
    
    def __init__(self, llm_client: LLMClient):
        """
        Initialize the batch Q&A processor.
        
        Args:
            llm_client: Initialized LLM client for answering questions
        """
        self.llm_client = llm_client
    
    def _format_answer_for_csv(self, answer: str) -> str:
        """
        Format LLM answer to be CSV-friendly.
        
        Args:
            answer: Raw answer from LLM
            
        Returns:
            Cleaned and formatted answer suitable for CSV
        """
        if not answer:
            return ""
        
        # Remove excessive whitespace and normalize line breaks
        lines = [line.strip() for line in answer.split('\n')]
        # Remove empty lines
        lines = [line for line in lines if line]
        # Join with space to create a single paragraph
        formatted = ' '.join(lines)
        
        # Remove any remaining multiple spaces
        while '  ' in formatted:
            formatted = formatted.replace('  ', ' ')
        
        return formatted.strip()
    
    def _create_structured_prompt(self, document_text: str, question: str) -> str:
        """
        Create a prompt that encourages concise, CSV-friendly responses.
        
        Args:
            document_text: The document content
            question: The question to ask
            
        Returns:
            Formatted prompt
        """
        prompt = f"""You are a helpful assistant that answers questions based on the provided document content.

Document Content:
{document_text}

Question: {question}

Please provide a clear, concise answer based on the document content. Format your response as follows:
- Use complete sentences but be concise
- If listing items, separate them with semicolons (;) not bullet points
- Keep the answer focused and to-the-point
- If the answer cannot be found in the document, state "Information not found in document"
- Do not use markdown formatting, bullet points, or numbered lists

Answer:"""
        
        return prompt
    
    def process_questions_batch(
        self,
        document_text: str,
        questions: List[str],
        document_name: str = "Unknown Document",
        model: str = None
    ) -> List[Dict[str, Any]]:
        """
        Process multiple questions for a single document.
        
        Args:
            document_text: Text content of the document
            questions: List of questions to ask
            document_name: Name of the document for reference
            model: Model to use for answering (optional)
            
        Returns:
            List of dictionaries containing question-answer pairs
        """
        results = []
        
        print(f"\nProcessing {len(questions)} questions for '{document_name}'...")
        
        for i, question in enumerate(questions, 1):
            print(f"  [{i}/{len(questions)}] Processing: {question[:50]}...")
            
            try:
                # Use structured prompt for better CSV formatting
                result = self.llm_client.ask_question_structured(
                    document_text=document_text,
                    question=question,
                    model=model
                )
                
                # Format the answer for CSV
                formatted_answer = self._format_answer_for_csv(result['answer'])
                
                results.append({
                    'document_name': document_name,
                    'question_number': i,
                    'question': question,
                    'answer': formatted_answer,
                    'model': result['model'],
                    'provider': result['provider'],
                    'status': 'success',
                    'error': None
                })
                
            except Exception as e:
                print(f"    ✗ Error: {str(e)}")
                results.append({
                    'document_name': document_name,
                    'question_number': i,
                    'question': question,
                    'answer': None,
                    'model': model,
                    'provider': self.llm_client.provider,
                    'status': 'error',
                    'error': str(e)
                })
        
        print(f"✓ Completed {len(results)} questions\n")
        return results
    
    def export_to_csv(
        self,
        results: List[Dict[str, Any]],
        output_path: str = None,
        include_timestamp: bool = True
    ) -> str:
        """
        Export Q&A results to a CSV file with proper formatting.
        
        Args:
            results: List of Q&A result dictionaries
            output_path: Path for the CSV file (optional, auto-generated if None)
            include_timestamp: Whether to include timestamp in filename
            
        Returns:
            Path to the created CSV file
        """
        if not results:
            raise ValueError("No results to export")
        
        # Generate output path if not provided
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") if include_timestamp else ""
            filename = f"qa_results_{timestamp}.csv" if timestamp else "qa_results.csv"
            output_path = os.path.join("outputs", filename)
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write to CSV with proper quoting
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'document_name',
                'question_number',
                'question',
                'answer',
                'model',
                'provider',
                'status',
                'error'
            ]
            
            writer = csv.DictWriter(
                csvfile, 
                fieldnames=fieldnames,
                quoting=csv.QUOTE_ALL  # Quote all fields for safety
            )
            writer.writeheader()
            
            for result in results:
                writer.writerow(result)
        
        print(f"✓ Results exported to: {output_path}")
        return output_path
    
    def process_multiple_documents_batch(
        self,
        documents: List[Dict[str, Any]],
        questions: List[str],
        model: str = None
    ) -> List[Dict[str, Any]]:
        """
        Process the same questions for multiple documents.
        
        Args:
            documents: List of document data dictionaries (from DocumentProcessor)
            questions: List of questions to ask each document
            model: Model to use for answering (optional)
            
        Returns:
            Combined list of all Q&A results
        """
        all_results = []
        
        print(f"\n{'='*60}")
        print(f"Batch Processing: {len(documents)} documents × {len(questions)} questions")
        print(f"{'='*60}\n")
        
        for doc_idx, doc_data in enumerate(documents, 1):
            print(f"[Document {doc_idx}/{len(documents)}] {doc_data['file_name']}")
            
            results = self.process_questions_batch(
                document_text=doc_data['text_content'],
                questions=questions,
                document_name=doc_data['file_name'],
                model=model
            )
            
            all_results.extend(results)
        
        print(f"\n{'='*60}")
        print(f"Completed: {len(all_results)} total Q&A pairs")
        print(f"{'='*60}\n")
        
        return all_results


# Example usage / test
def main():
    """Test function demonstrating batch Q&A processing."""
    from document_processor import DocumentProcessor
    
    # Initialize processors
    doc_processor = DocumentProcessor()
    llm_client = LLMClient(provider="ollama")
    batch_processor = BatchQAProcessor(llm_client)
    
    # Process a document (using cache if available)
    print("Loading document...")
    doc_data = doc_processor.process_document("documents/ghana_gonja_marriage.pdf")
    
    # Define batch questions
    questions = [
        "What is the main topic of this document?",
        "What are the key findings or conclusions?",
        "Are there any important dates or time periods mentioned?",
        "What methodology was used in this research?",
        "What are the main recommendations?"
    ]
    
    # Process questions in batch
    results = batch_processor.process_questions_batch(
        document_text=doc_data['text_content'],
        questions=questions,
        document_name=doc_data['file_name'],
        model="gemma2:2b"
    )
    
    # Export to CSV
    csv_path = batch_processor.export_to_csv(results)
    
    print(f"\n✓ All done! Check {csv_path} for results.")


if __name__ == "__main__":
    main()