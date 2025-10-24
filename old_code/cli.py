#!/usr/bin/env python3
"""
Command-line interface for the Document Q&A System.
"""

import asyncio
import argparse
import os
import sys
from typing import Optional
from dotenv import load_dotenv

from document_processor import DocumentProcessor
from llm_client import LLMClient

load_dotenv()


class DocumentQACLI:
    """Command-line interface for document Q&A functionality."""
    
    def __init__(self):
        self.doc_processor = DocumentProcessor()
        self.llm_client = None
        self.current_document = None
    
    def initialize_llm(self, provider: str = "openai"):
        """Initialize the LLM client."""
        try:
            self.llm_client = LLMClient(provider)
            print(f"✅ LLM client initialized with {provider}")
            return True
        except ValueError as e:
            print(f"❌ Error initializing LLM client: {e}")
            print("Please set up your API keys in the environment variables.")
            return False
    
    async def process_document(self, file_path: str) -> bool:
        """Process a document file."""
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return False
        
        if not self.doc_processor.is_supported(file_path):
            print(f"❌ Unsupported file format. Supported formats: {', '.join(self.doc_processor.SUPPORTED_EXTENSIONS)}")
            return False
        
        try:
            print(f"📄 Processing document: {file_path}")
            self.current_document = await self.doc_processor.process_document(file_path)
            
            print(f"✅ Document processed successfully!")
            print(f"   File: {self.current_document['file_name']}")
            print(f"   Words: {self.current_document['word_count']}")
            print(f"   Characters: {self.current_document['char_count']}")
            
            return True
        
        except Exception as e:
            print(f"❌ Error processing document: {e}")
            return False
    
    async def ask_question(self, question: str) -> bool:
        """Ask a question about the current document."""
        if not self.current_document:
            print("❌ No document loaded. Please process a document first.")
            return False
        
        if not self.llm_client:
            print("❌ LLM client not initialized. Please check your API keys.")
            return False
        
        try:
            print(f"❓ Question: {question}")
            print("🤔 Thinking...")
            
            result = await self.llm_client.ask_question(
                self.current_document["text_content"], 
                question
            )
            
            print(f"\n💡 Answer:")
            print(f"{result['answer']}")
            print(f"\n📊 Powered by {result['provider']} ({result['model']})")
            
            return True
        
        except Exception as e:
            print(f"❌ Error processing question: {e}")
            return False
    
    async def interactive_mode(self):
        """Run in interactive mode."""
        print("🚀 Document Q&A System - Interactive Mode")
        print("=" * 50)
        
        # Initialize LLM
        provider = os.getenv("DEFAULT_LLM_PROVIDER", "openai")
        if not self.initialize_llm(provider):
            return
        
        # Get document path
        while True:
            file_path = input("\n📁 Enter document path (or 'quit' to exit): ").strip()
            
            if file_path.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                return
            
            if await self.process_document(file_path):
                break
        
        # Interactive Q&A loop
        print(f"\n💬 You can now ask questions about '{self.current_document['file_name']}'")
        print("Type 'quit' to exit, 'new' to load a new document")
        
        while True:
            question = input("\n❓ Your question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if question.lower() == 'new':
                new_file = input("📁 Enter new document path: ").strip()
                if await self.process_document(new_file):
                    print(f"💬 You can now ask questions about '{self.current_document['file_name']}'")
                continue
            
            if question:
                await self.ask_question(question)


async def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="Document Q&A System CLI")
    parser.add_argument("--file", "-f", help="Path to document file")
    parser.add_argument("--question", "-q", help="Question to ask about the document")
    parser.add_argument("--provider", "-p", choices=["openai", "anthropic"], 
                       default=os.getenv("DEFAULT_LLM_PROVIDER", "openai"),
                       help="LLM provider to use")
    parser.add_argument("--interactive", "-i", action="store_true",
                       help="Run in interactive mode")
    
    args = parser.parse_args()
    
    cli = DocumentQACLI()
    
    # Interactive mode
    if args.interactive:
        await cli.interactive_mode()
        return
    
    # Single question mode
    if not args.file:
        print("❌ Error: Document file is required (use --file or --interactive)")
        sys.exit(1)
    
    if not args.question:
        print("❌ Error: Question is required (use --question or --interactive)")
        sys.exit(1)
    
    # Initialize LLM
    if not cli.initialize_llm(args.provider):
        sys.exit(1)
    
    # Process document
    if not await cli.process_document(args.file):
        sys.exit(1)
    
    # Ask question
    success = await cli.ask_question(args.question)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
