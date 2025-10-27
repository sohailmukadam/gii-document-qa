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
    """Handles PDF document processing with caching."""
    def __init__(self, cache_dir: str = "document_cache"):
        """Initialize with cache directory."""
        self.cache_dir = cache_dir
        self.cache_index_path = os.path.join(cache_dir, "cache_index.json")
        os.makedirs(cache_dir, exist_ok=True)
        self.cache_index = self._load_cache_index()
    
    def process_document(self, file_path: str, force_reprocess: bool = False) -> Dict[str, Any]:
        """Process a PDF document, using cache when available."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        if not file_path.lower().endswith('.pdf'):
            raise ValueError(f"Only PDF files supported")
        
        # Check cache
        file_hash = self._hash_file(file_path)
        if not force_reprocess:
            cached = self._get_from_cache(file_hash, file_path)
            if cached:
                return cached
        
        # Process document
        print(f"Processing: {os.path.basename(file_path)}...")
        text_content = self._extract_pdf_text(file_path)
        
        # Build result
        result = {
            'file_path': file_path,
            'file_name': os.path.basename(file_path),
            'file_extension': '.pdf',
            'text_content': text_content,
            'word_count': len(text_content.split()),
            'char_count': len(text_content),
            'from_cache': False,
            'file_hash': file_hash
        }
        
        # Cache it
        self._save_to_cache(file_hash, result)
        return result
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF (with OCR for scanned pages)."""
        text_content = ""
        try:
            doc = fitz.open(file_path)
            for page_num, page in enumerate(doc, 1):
                print(f"  Page {page_num}/{len(doc)}", end='')
            
                # Try extracting text first
                text = page.get_text()    
                if text.strip():
                    text_content += text + "\n"
                else:
                    # Use OCR for scanned pages
                    print(" (OCR)", end='')
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                    img = Image.open(io.BytesIO(pix.tobytes("png")))
                    text_content += pytesseract.image_to_string(img) + "\n"
            doc.close()
            return text_content.strip()
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")
    
    def _hash_file(self, file_path: str) -> str:
        """Compute SHA256 hash of file."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def _get_from_cache(self, file_hash: str, file_path: str) -> Optional[Dict[str, Any]]:
        """Retrieve from cache if available."""
        if file_hash not in self.cache_index:
            return None
        cache_file = os.path.join(self.cache_dir, f"{file_hash}.txt")
        if not os.path.exists(cache_file):
            return None
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                text_content = f.read()
            entry = self.cache_index[file_hash]
            print(f"Using cached: {os.path.basename(file_path)}")
            return {
                'file_path': file_path,
                'file_name': entry['file_name'],
                'file_extension': '.pdf',
                'text_content': text_content,
                'word_count': entry['word_count'],
                'char_count': entry['char_count'],
                'from_cache': True,
                'file_hash': file_hash
            }
        except Exception as e:
            print(f"Warning: Cache read failed: {e}")
            return None
    
    def _save_to_cache(self, file_hash: str, document_data: Dict[str, Any]):
        """Save to cache."""
        cache_file = os.path.join(self.cache_dir, f"{file_hash}.txt")
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                f.write(document_data['text_content'])
            self.cache_index[file_hash] = {
                'file_path': document_data['file_path'],
                'file_name': document_data['file_name'],
                'file_extension': '.pdf',
                'word_count': document_data['word_count'],
                'char_count': document_data['char_count']
            }
            self._save_cache_index()
            print(f"✓ Cached: {document_data['file_name']}")
        except Exception as e:
            print(f"Warning: Cache save failed: {e}")
    
    def _load_cache_index(self) -> Dict[str, Any]:
        """Load cache index from disk."""
        if os.path.exists(self.cache_index_path):
            try:
                with open(self.cache_index_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_cache_index(self):
        """Save cache index to disk."""
        try:
            with open(self.cache_index_path, 'w', encoding='utf-8') as f:
                json.dump(self.cache_index, f, indent=2)
        except Exception as e:
            print(f"Warning: Cache index save failed: {e}")
    
    def clear_cache(self):
        """Clear all cached documents."""
        for file_hash in list(self.cache_index.keys()):
            cache_file = os.path.join(self.cache_dir, f"{file_hash}.txt")
            if os.path.exists(cache_file):
                os.remove(cache_file)
        self.cache_index = {}
        self._save_cache_index()
        print("Cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_size = 0
        for file_hash in self.cache_index.keys():
            cache_file = os.path.join(self.cache_dir, f"{file_hash}.txt")
            if os.path.exists(cache_file):
                total_size += os.path.getsize(cache_file)
        return {
            'total_cached_files': len(self.cache_index),
            'total_cache_size_bytes': total_size,
            'total_cache_size_mb': total_size / (1024 * 1024),
            'cache_directory': self.cache_dir
        }