"""
Document processing module for extracting text from PDF files with caching.
"""

import os
import hashlib
import json
from typing import Dict, Any, Optional
import fitz
import pytesseract
from PIL import Image
import io

pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'

class DocumentProcessor:
    """Handles document processing for PDF files with caching."""
    
    SUPPORTED_EXTENSIONS = {'.pdf'}
    CACHE_DIR = "document_cache"
    CACHE_INDEX_FILE = "cache_index.json"
    
    def __init__(self, cache_dir: str = None):
        """
        Initialize the document processor with caching.
        
        Args:
            cache_dir: Directory to store cached documents (default: 'document_cache')
        """
        self.cache_dir = cache_dir or self.CACHE_DIR
        self.cache_index_path = os.path.join(self.cache_dir, self.CACHE_INDEX_FILE)
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Load cache index
        self.cache_index = self._load_cache_index()
        
        self.processors = {
            '.pdf': self._process_pdf
        }
    
    def _load_cache_index(self) -> Dict[str, Any]:
        """Load the cache index from disk."""
        if os.path.exists(self.cache_index_path):
            try:
                with open(self.cache_index_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load cache index: {e}")
                return {}
        return {}
    
    def _save_cache_index(self):
        """Save the cache index to disk."""
        try:
            with open(self.cache_index_path, 'w', encoding='utf-8') as f:
                json.dump(self.cache_index, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save cache index: {e}")
    
    def _compute_file_hash(self, file_path: str) -> str:
        """
        Compute SHA256 hash of a file for cache lookup.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Hexadecimal hash string
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            # Read in chunks to handle large files
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _get_cached_document(self, file_hash: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached document data if it exists.
        
        Args:
            file_hash: Hash of the document file
            
        Returns:
            Document data dictionary or None if not cached
        """
        if file_hash in self.cache_index:
            cache_entry = self.cache_index[file_hash]
            cache_text_path = os.path.join(self.cache_dir, f"{file_hash}.txt")
            
            if os.path.exists(cache_text_path):
                try:
                    with open(cache_text_path, 'r', encoding='utf-8') as f:
                        text_content = f.read()
                    
                    print(f"✓ Using cached document: {cache_entry['file_name']}")
                    return {
                        'file_path': cache_entry['file_path'],
                        'file_name': cache_entry['file_name'],
                        'file_extension': cache_entry['file_extension'],
                        'text_content': text_content,
                        'word_count': cache_entry['word_count'],
                        'char_count': cache_entry['char_count'],
                        'from_cache': True,
                        'file_hash': file_hash
                    }
                except Exception as e:
                    print(f"Warning: Could not read cached file: {e}")
        
        return None
    
    def _cache_document(self, file_hash: str, document_data: Dict[str, Any]):
        """
        Cache a processed document.
        
        Args:
            file_hash: Hash of the document file
            document_data: Processed document data
        """
        cache_text_path = os.path.join(self.cache_dir, f"{file_hash}.txt")
        
        try:
            # Save text content to file
            with open(cache_text_path, 'w', encoding='utf-8') as f:
                f.write(document_data['text_content'])
            
            # Update cache index
            self.cache_index[file_hash] = {
                'file_path': document_data['file_path'],
                'file_name': document_data['file_name'],
                'file_extension': document_data['file_extension'],
                'word_count': document_data['word_count'],
                'char_count': document_data['char_count']
            }
            
            # Save index
            self._save_cache_index()
            
            print(f"✓ Document cached: {document_data['file_name']}")
            
        except Exception as e:
            print(f"Warning: Could not cache document: {e}")
    
    def process_document(self, file_path: str, force_reprocess: bool = False) -> Dict[str, Any]:
        """
        Process a document and extract text content, using cache when available.
        
        Args:
            file_path: Path to the document file
            force_reprocess: If True, ignore cache and reprocess the document
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        # Compute file hash for cache lookup
        file_hash = self._compute_file_hash(file_path)
        
        # Check cache unless force reprocess
        if not force_reprocess:
            cached_data = self._get_cached_document(file_hash)
            if cached_data:
                # Update file_path to current path (in case file was moved)
                cached_data['file_path'] = file_path
                return cached_data
        
        # Process the document
        print(f"Processing document: {os.path.basename(file_path)}...")
        processor = self.processors[file_ext]
        text_content = processor(file_path)
        
        document_data = {
            'file_path': file_path,
            'file_name': os.path.basename(file_path),
            'file_extension': file_ext,
            'text_content': text_content,
            'word_count': len(text_content.split()) if text_content else 0,
            'char_count': len(text_content) if text_content else 0,
            'from_cache': False,
            'file_hash': file_hash
        }
        
        # Cache the processed document
        self._cache_document(file_hash, document_data)
        
        return document_data

    def _process_pdf(self, file_path: str) -> str:
        """Extract text from PDF using PyMuPDF with OCR for scanned pages."""
        try:
            text_content = ""
            doc = fitz.open(file_path)
            
            for page_num, page in enumerate(doc, 1):
                print(f"  Processing page {page_num}/{len(doc)}...")
                
                # Try to get embedded text first
                text = page.get_text()
                
                if text.strip():
                    # Text found - it's a regular PDF page
                    text_content += text + "\n"
                else:
                    # No text - it's a scanned page, use OCR
                    print(f"    → Scanned page detected, using OCR...")
                    
                    # Convert page to image
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                    img_data = pix.tobytes("png")
                    img = Image.open(io.BytesIO(img_data))
                    
                    # Use OCR to read the image
                    ocr_text = pytesseract.image_to_string(img)
                    text_content += ocr_text + "\n"
            
            doc.close()
            return text_content.strip()
            
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")
    
    def is_supported(self, file_path: str) -> bool:
        """Check if file format is supported."""
        file_ext = os.path.splitext(file_path)[1].lower()
        return file_ext in self.SUPPORTED_EXTENSIONS
    
    def clear_cache(self):
        """Clear all cached documents."""
        try:
            # Remove all cached text files
            for file_hash in self.cache_index.keys():
                cache_text_path = os.path.join(self.cache_dir, f"{file_hash}.txt")
                if os.path.exists(cache_text_path):
                    os.remove(cache_text_path)
            
            # Clear index
            self.cache_index = {}
            self._save_cache_index()
            
            print("✓ Cache cleared successfully")
            
        except Exception as e:
            print(f"Error clearing cache: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get statistics about the cache."""
        total_files = len(self.cache_index)
        total_size = 0
        
        for file_hash in self.cache_index.keys():
            cache_text_path = os.path.join(self.cache_dir, f"{file_hash}.txt")
            if os.path.exists(cache_text_path):
                total_size += os.path.getsize(cache_text_path)
        
        return {
            'total_cached_files': total_files,
            'total_cache_size_bytes': total_size,
            'total_cache_size_mb': total_size / (1024 * 1024),
            'cache_directory': self.cache_dir
        }