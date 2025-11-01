# Document Q&A System

An automated question-answering system for generating training datasets from PDF documents using Google Gemini AI. This tool streamlines the process of extracting information from multiple documents by processing batches of questions concurrently and exporting results to CSV format.

## Features

- **PDF Document Processing**: Extracts text from PDFs with OCR support for scanned documents
- **Intelligent Caching**: Avoids reprocessing previously uploaded documents
- **Batch Question Processing**: Process multiple questions across multiple documents simultaneously
- **Google Gemini Integration**: Leverages Gemini 2.0 Flash Lite for fast, accurate responses
- **CSV Export**: Exports Q&A pairs in a structured CSV format for dataset creation
- **Web Interface**: User-friendly Streamlit interface for document upload and batch processing

## Prerequisites

- Python 3.8 or higher
- Tesseract OCR (for scanned PDF support)
- Google Gemini API key

### Installing Tesseract OCR

**macOS:**
```bash
brew install tesseract
```

**Windows:**
Download and install from [GitHub Tesseract Releases](https://github.com/UB-Mannheim/tesseract/wiki)

## Installation

1. **Clone the repository:**
```bash
git clone git@github.com:sohailmukadam/gii-document-qa.git
cd gii-document-qa
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure Tesseract path (if needed):**

Edit `document_processor.py` and update the tesseract path for your system:
```python
pytesseract.pytesseract.tesseract_cmd = r'/path/to/your/tesseract'
```

4. **Set up environment variables:**

Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_api_key_here
```

To obtain a Gemini API key, visit [Google AI Studio](https://makersuite.google.com/app/apikey).

## Usage

### Starting the Application

Run the Streamlit application:
```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`.

### Workflow

1. **Upload Documents**
   - Navigate to the "Document Upload" tab
   - Select one or more PDF files
   - Click "Process Documents"
   - Previously processed documents will load from cache automatically

2. **Batch Processing**
   - Navigate to the "Batch Processing" tab
   - Enter your questions (one per line) in the text area
   - Click "Process" to generate Q&A pairs
   - Download results as CSV when processing completes

### Example Questions

```
What is the main research objective?
What methodology was employed?
What are the key findings?
Who are the primary authors?
What datasets were used in this study?
```

## Project Structure

```
document-qa-system/
│
├── app.py                     # Main Streamlit application
├── document_processor.py      # PDF processing and caching logic
├── llm_client.py              # Google Gemini API integration
├── batch_qa_processor.py      # Batch Q&A processing logic
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (create this)
│
├── document_cache/            # Cached document data (auto-created)
│   ├── cache_index.json       # Cache metadata
│   └── *.txt                  # Cached document texts
│
└── outputs/                   # Generated CSV files (auto-created)
    └── qa_results_*.csv       # Timestamped Q&A results
```

## Configuration

### Model Selection

The application defaults to `gemini-2.0-flash-lite` for optimal speed and cost-effectiveness. You can select different models from the sidebar if available.

### Cache Management

- **View Cache Stats**: Check the sidebar for cache statistics
- **Clear Cache**: Use the "Clear Cache" button to remove all cached documents
- **Force Reprocess**: Delete cache and re-upload documents to force reprocessing

## Output Format

CSV files include the following columns:

| Column | Description |
|--------|-------------|
| `document_name` | Name of the source PDF document |
| `question_number` | Sequential question number |
| `question` | The question text |
| `answer` | Generated answer from Gemini |
| `model` | Model used for generation |
| `provider` | LLM provider (gemini) |
| `status` | Processing status (success/error) |
| `error` | Error message if processing failed |

## API Usage Example

For programmatic usage without the web interface:

```python
from document_processor import DocumentProcessor
from llm_client import LLMClient
from batch_qa_processor import BatchQAProcessor

# Initialize components
doc_processor = DocumentProcessor()
llm_client = LLMClient(provider="gemini")
batch_processor = BatchQAProcessor(llm_client)

# Process a document
doc_data = doc_processor.process_document("path/to/document.pdf")

# Define questions
questions = [
    "What is the main topic?",
    "Who are the authors?",
    "What are the key findings?"
]

# Process questions
results = batch_processor.process_single_document(
    document_text=doc_data['text_content'],
    questions=questions,
    document_name=doc_data['file_name'],
    model="gemini-2.0-flash-lite"
)

# Export to CSV
csv_path = batch_processor.export_to_csv(results)
```

## Troubleshooting

### Common Issues

**Issue: "API key required" error**
- Ensure your `.env` file contains a valid `GEMINI_API_KEY`
- Check that the `.env` file is in the project root directory

**Issue: Tesseract not found**
- Install Tesseract OCR for your operating system
- Update the `tesseract_cmd` path in `document_processor.py`

**Issue: Poor OCR quality**
- Ensure source PDFs are high resolution
- Consider pre-processing scanned documents for better OCR results

**Issue: Rate limit errors**
- Reduce the number of questions or documents processed at once
- Wait a few minutes between large batch operations.