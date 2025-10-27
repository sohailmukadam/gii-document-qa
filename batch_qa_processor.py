"""
Simplified batch Q&A processor with concurrent processing.
"""

import csv
import os
from typing import List, Dict, Any
from datetime import datetime
from llm_client import LLMClient


class BatchQAProcessor:
    """Handles batch question processing with concurrent execution."""
    
    def __init__(self, llm_client: LLMClient):
        """Initialize the batch Q&A processor."""
        self.llm_client = llm_client
    
    def process_single_document(self, document_text: str, questions: List[str],
                               document_name: str, model: str = "gemma2:2b") -> List[Dict[str, Any]]:
        """
        Process multiple questions for a single document (concurrent).
        
        Args:
            document_text: Text content of the document
            questions: List of questions to ask
            document_name: Name of the document
            model: Model to use
            
        Returns:
            List of Q&A result dictionaries
        """
        print(f"\nProcessing {len(questions)} questions for '{document_name}'...")
        
        # Use concurrent batch processing
        results = self.llm_client.ask_questions_batch(document_text, questions, model)
        
        # Format results with metadata
        formatted_results = []
        for i, (question, result) in enumerate(zip(questions, results), 1):
            formatted_results.append({
                'document_name': document_name,
                'question_number': i,
                'question': question,
                'answer': result.get('answer', ''),
                'model': result['model'],
                'provider': result['provider'],
                'status': 'error' if result.get('error') else 'success',
                'error': result.get('error')
            })
        
        success_count = sum(1 for r in formatted_results if r['status'] == 'success')
        print(f"✓ Completed: {success_count}/{len(questions)} successful")
        
        return formatted_results
    
    def process_multiple_documents_batch(self, documents: List[Dict[str, Any]],
                                        questions: List[str],
                                        model: str = "gemma2:2b") -> List[Dict[str, Any]]:
        """
        Process questions for multiple documents.
        
        Args:
            documents: List of document data dictionaries
            questions: List of questions
            model: Model to use
            
        Returns:
            Combined list of all Q&A results
        """
        print(f"\n{'='*60}")
        print(f"Batch Processing: {len(documents)} documents × {len(questions)} questions")
        print(f"{'='*60}")
        
        all_results = []
        
        for idx, doc in enumerate(documents, 1):
            print(f"\n[Document {idx}/{len(documents)}] {doc['file_name']}")
            
            results = self.process_single_document(
                document_text=doc['text_content'],
                questions=questions,
                document_name=doc['file_name'],
                model=model
            )
            
            all_results.extend(results)
        
        print(f"\n{'='*60}")
        print(f"Total completed: {len(all_results)} Q&A pairs")
        print(f"{'='*60}\n")
        
        return all_results
    
    def export_to_csv(self, results: List[Dict[str, Any]], 
                     output_path: str = None) -> str:
        """
        Export results to CSV file.
        
        Args:
            results: List of Q&A result dictionaries
            output_path: Output path (auto-generated if None)
            
        Returns:
            Path to the created CSV file
        """
        if not results:
            raise ValueError("No results to export")
        
        # Generate output path
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join("outputs", f"qa_results_{timestamp}.csv")
        
        # Create output directory
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write CSV
        fieldnames = ['document_name', 'question_number', 'question', 'answer', 
                     'model', 'provider', 'status', 'error']
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            writer.writerows(results)
        
        print(f"✓ Results exported to: {output_path}")
        return output_path