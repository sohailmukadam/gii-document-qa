# Document Q&A System

A powerful system that allows you to upload PDF documents and ask questions about their content using Large Language Models (LLMs). The system features a Streamlit dashboard with OCR capabilities for scanned PDFs.

## Features

- 📄 **PDF Processing**: Supports PDF documents with OCR for scanned pages
- 🤖 **Multiple LLM Providers**: Works with OpenAI GPT models and Anthropic Claude models
- 🎨 **Streamlit Dashboard**: Beautiful, interactive web interface for document upload and Q&A
- 🔍 **OCR Capabilities**: Automatically detects and processes scanned PDF pages using Tesseract
- ⚡ **Fast Processing**: Efficient document processing and text extraction
- 🔒 **Secure**: Local document processing with optional cloud LLM APIs

## Supported Document Formats

- **PDF** (.pdf) - Extracts text from PDF documents with automatic OCR for scanned pages

## Supported LLM Providers

- **OpenAI**: GPT-3.5-turbo, GPT-4, GPT-4-turbo-preview
- **Anthropic**: Claude-3-haiku, Claude-3-sonnet, Claude-3-opus

## Installation

1. **Clone or download the project**:
   ```bash
   git clone <repository-url>
   cd gii-document-qa
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp env_example.txt .env
   ```
   
   Edit `.env` and add your API keys:
   ```env
   # For OpenAI
   OPENAI_API_KEY=your_openai_api_key_here
   
   # For Anthropic
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   
   # Default provider
   DEFAULT_LLM_PROVIDER=openai
   
   # Upload directory
   UPLOAD_DIR=uploads
   ```

## Usage

### Streamlit Dashboard (Recommended)

1. **Start the Streamlit dashboard**:
   ```bash
   streamlit run streamlit_app.py
   ```
   
   Or use the startup script:
   ```bash
   chmod +x run_streamlit.sh
   ./run_streamlit.sh
   ```

2. **Open your browser** and go to `http://localhost:8501`

3. **Upload a PDF document** using the file uploader

4. **Process the document** by clicking "Process Document"

5. **Ask questions** about your document in the Q&A section

### Command Line Interface

#### Interactive Mode
```bash
python cli.py --interactive
```

#### Single Question Mode
```bash
python cli.py --file document.pdf --question "What is this document about?"
```

#### CLI Options
```bash
python cli.py --help
```

**Available options:**
- `--file, -f`: Path to document file
- `--question, -q`: Question to ask about the document
- `--provider, -p`: LLM provider (openai or anthropic)
- `--interactive, -i`: Run in interactive mode

### Examples

#### Streamlit Dashboard Examples
1. Upload a PDF research paper and ask: "What are the main findings?"
2. Upload a scanned contract and ask: "What are the key terms and conditions?"
3. Upload a manual and ask: "How do I troubleshoot issue X?"

#### CLI Examples
```bash
# Ask a single question
python cli.py --file report.pdf --question "What are the key recommendations?"

# Use Anthropic Claude instead of OpenAI
python cli.py --file contract.docx --question "What are the payment terms?" --provider anthropic

# Interactive mode for multiple questions
python cli.py --interactive
```

## API Endpoints

The web interface provides the following REST API endpoints:

- `GET /`: Home page
- `POST /upload`: Upload and process a document
- `POST /ask`: Ask a question about the current document
- `GET /document-info`: Get information about the current document
- `DELETE /clear-document`: Clear the current document
- `GET /health`: Health check endpoint

## Project Structure

```
gii-document-qa/
├── streamlit_app.py       # Streamlit dashboard (main interface)
├── document_processor.py  # PDF processing with OCR module
├── llm_client_sync.py     # Synchronous LLM integration module
├── llm_client.py          # Asynchronous LLM integration module
├── cli.py                 # Command-line interface
├── requirements.txt       # Python dependencies
├── env_example.txt        # Environment variables example
├── run_streamlit.sh       # Streamlit startup script
├── documents/             # Sample documents directory
└── README.md             # This file
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required for OpenAI |
| `ANTHROPIC_API_KEY` | Anthropic API key | Required for Anthropic |
| `DEFAULT_LLM_PROVIDER` | Default LLM provider | `openai` |
| `UPLOAD_DIR` | Directory for uploaded files | `uploads` |

### LLM Models

**OpenAI Models:**
- `gpt-3.5-turbo` (default)
- `gpt-4`
- `gpt-4-turbo-preview`

**Anthropic Models:**
- `claude-3-haiku-20240307`
- `claude-3-sonnet-20240229` (default)
- `claude-3-opus-20240229`

## Troubleshooting

### Common Issues

1. **"LLM client not configured" error**:
   - Make sure you've set up your API keys in the `.env` file
   - Verify the API keys are valid and have sufficient credits

2. **"Unsupported file format" error**:
   - Only PDF files are supported
   - Ensure the file is not corrupted

3. **"Error processing document" error**:
   - For PDFs: The system will automatically use OCR for scanned pages
   - Ensure Tesseract OCR is installed: `brew install tesseract` (macOS)
   - Check file permissions

4. **Streamlit dashboard not loading**:
   - Make sure port 8501 is available
   - Check that all dependencies are installed
   - Verify Tesseract is installed for OCR functionality

5. **OCR not working**:
   - Install Tesseract OCR: `brew install tesseract` (macOS) or `sudo apt-get install tesseract-ocr` (Ubuntu)
   - The system automatically detects scanned pages and uses OCR

### Getting API Keys

**OpenAI API Key:**
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key

**Anthropic API Key:**
1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key

## Development

### Adding New Document Formats

To add support for new document formats:

1. Add the file extension to `SUPPORTED_EXTENSIONS` in `document_processor.py`
2. Implement a new processor method (e.g., `_process_md` for Markdown)
3. Add the processor to the `processors` dictionary
4. Update the Streamlit app file uploader to accept the new format

### Adding New LLM Providers

To add support for new LLM providers:

1. Install the provider's Python SDK
2. Add provider initialization in `llm_client.py`
3. Implement the `_ask_provider` method
4. Add the provider to `get_available_models()`

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## Support

If you encounter any issues or have questions, please:
1. Check the troubleshooting section above
2. Search existing issues
3. Create a new issue with detailed information about your problem
