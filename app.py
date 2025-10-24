"""
Streamlit Dashboard for Document Q&A System with CSV-Optimized Output
"""

import streamlit as st
import os
import tempfile
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime

from document_processor import DocumentProcessor
from llm_client import LLMClient
from batch_qa_processor import BatchQAProcessor

# Page configuration
st.set_page_config(
    page_title="Document Q&A Analysis System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS styling
st.markdown("""
<style>
    /* Main header styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: 600;
        text-align: center;
        margin-bottom: 1rem;
        color: #1a1a1a;
        letter-spacing: -0.5px;
    }
    
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Metric cards */
    .metric-card {
        background-color: #f8f9fa;
        padding: 1.2rem;
        border-radius: 8px;
        border-left: 4px solid #2c5aa0;
        margin-bottom: 1rem;
    }
    
    /* Answer display box */
    .answer-box {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        margin-top: 1rem;
        line-height: 1.6;
    }
    
    /* Status indicators */
    .status-online {
        color: #28a745;
        font-weight: 600;
    }
    
    .status-offline {
        color: #dc3545;
        font-weight: 600;
    }
    
    .cache-badge {
        background-color: #28a745;
        color: white;
        padding: 0.25rem 0.6rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Info boxes */
    .info-box {
        background-color: #e7f3ff;
        border-left: 4px solid #2196F3;
        padding: 1.2rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    
    .info-box ul {
        margin-top: 0.5rem;
        margin-bottom: 0;
    }
    
    .info-box li {
        margin-bottom: 0.3rem;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #2c3e50;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #e9ecef;
        padding-bottom: 0.5rem;
    }
    
    /* Tips section */
    .tips-section {
        background-color: #f8f9fa;
        padding: 1.2rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        margin-top: 1.5rem;
    }
    
    .tips-section strong {
        color: #2c5aa0;
    }
    
    /* Button styling improvements */
    .stButton > button {
        border-radius: 4px;
        font-weight: 500;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        padding-top: 1rem;
    }
    
    /* Dataframe styling */
    .dataframe {
        font-size: 0.9rem;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        font-weight: 500;
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'documents' not in st.session_state:
    st.session_state.documents = []
if 'llm_client' not in st.session_state:
    st.session_state.llm_client = None
if 'batch_processor' not in st.session_state:
    st.session_state.batch_processor = None
if 'selected_model' not in st.session_state:
    st.session_state.selected_model = "gemma2:2b"
if 'batch_questions' not in st.session_state:
    st.session_state.batch_questions = ""


def initialize_clients():
    """Initialize LLM client and batch processor if not already done."""
    if st.session_state.llm_client is None:
        try:
            st.session_state.llm_client = LLMClient(provider="ollama")
            st.session_state.batch_processor = BatchQAProcessor(st.session_state.llm_client)
            return True
        except ValueError as e:
            st.error(f"Error initializing LLM client: {e}")
            st.info("Please ensure Ollama is installed and running.")
            return False
    return True


def process_uploaded_files(uploaded_files) -> List[Dict[str, Any]]:
    """Process multiple uploaded files and return document data."""
    doc_processor = DocumentProcessor()
    processed_docs = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, uploaded_file in enumerate(uploaded_files):
        status_text.text(f"Processing {idx + 1}/{len(uploaded_files)}: {uploaded_file.name}")
        
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        try:
            # Process the document (will use cache if available)
            document_data = doc_processor.process_document(tmp_file_path)
            processed_docs.append(document_data)
            
            # Clean up temporary file
            os.unlink(tmp_file_path)
            
        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {str(e)}")
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
        
        progress_bar.progress((idx + 1) / len(uploaded_files))
    
    status_text.text("All documents processed successfully")
    progress_bar.empty()
    status_text.empty()
    
    return processed_docs


def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<h1 class="main-header">Document Q&A Analysis System</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Automated Question-Answering for Research Documents</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("System Configuration")
        
        # LLM Provider
        st.info("**LLM Provider:** Ollama (Local Deployment)")
        
        # Initialize clients
        llm_available = initialize_clients()
        
        if llm_available:
            st.markdown('<p class="status-online">Status: Online</p>', unsafe_allow_html=True)
            
            # Model selection
            available_models = st.session_state.llm_client.get_available_models()
            model_list = available_models.get("ollama", [])
            
            if model_list:
                selected_model = st.selectbox(
                    "Model Selection:",
                    model_list,
                    index=model_list.index(st.session_state.selected_model) if st.session_state.selected_model in model_list else 0
                )
                st.session_state.selected_model = selected_model
            else:
                st.warning("No models detected. Use 'ollama pull <model>' to install models.")
        else:
            st.markdown('<p class="status-offline">Status: Offline</p>', unsafe_allow_html=True)
            st.error("Please start Ollama service: `ollama serve`")
        
        st.divider()
        
        # Cache statistics
        st.subheader("Cache Statistics")
        doc_processor = DocumentProcessor()
        cache_stats = doc_processor.get_cache_stats()
        st.metric("Cached Documents", cache_stats['total_cached_files'])
        st.metric("Cache Size", f"{cache_stats['total_cache_size_mb']:.2f} MB")
        
        if st.button("Clear Cache", type="secondary"):
            doc_processor.clear_cache()
            st.success("Cache cleared successfully")
            st.rerun()
        
        st.divider()
        
        # Document info
        if st.session_state.documents:
            st.subheader("Loaded Documents")
            for doc in st.session_state.documents:
                with st.expander(doc['file_name']):
                    st.write(f"**Words:** {doc['word_count']:,}")
                    st.write(f"**Characters:** {doc['char_count']:,}")
                    if doc.get('from_cache', False):
                        st.markdown('<span class="cache-badge">Cached</span>', unsafe_allow_html=True)
            
            if st.button("Clear All Documents", type="secondary"):
                st.session_state.documents = []
                st.rerun()
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["Document Upload", "Single Question Query", "Batch Processing"])
    
    # Tab 1: Upload Documents
    with tab1:
        st.subheader("Document Upload Interface")
        
        uploaded_files = st.file_uploader(
            "Select PDF Documents",
            type=['pdf'],
            accept_multiple_files=True,
            help="Upload one or more PDF documents. Previously processed documents will be loaded from cache for faster processing."
        )
        
        if uploaded_files:
            st.info(f"{len(uploaded_files)} file(s) selected for processing")
            
            if st.button("Process Documents", type="primary"):
                with st.spinner("Processing documents..."):
                    processed_docs = process_uploaded_files(uploaded_files)
                    
                    if processed_docs:
                        st.session_state.documents = processed_docs
                        
                        # Show summary
                        cached_count = sum(1 for doc in processed_docs if doc.get('from_cache', False))
                        st.success(f"Successfully processed {len(processed_docs)} document(s)")
                        if cached_count > 0:
                            st.info(f"{cached_count} document(s) loaded from cache (optimized processing)")
                        
                        st.rerun()
    
    # Tab 2: Single Question Mode
    with tab2:
        st.subheader("Single Question Query Interface")
        
        if not st.session_state.documents:
            st.info("Please upload and process documents in the Document Upload tab before proceeding.")
        elif not llm_available:
            st.error("LLM client unavailable. Please ensure Ollama is running.")
        else:
            # Document selection
            doc_names = [doc['file_name'] for doc in st.session_state.documents]
            selected_doc_name = st.selectbox("Select Document:", doc_names)
            selected_doc = next(doc for doc in st.session_state.documents if doc['file_name'] == selected_doc_name)
            
            # Question input
            question = st.text_area(
                "Enter Research Question:",
                placeholder="Example: What is the primary research objective of this study?",
                height=100
            )
            
            if st.button("Submit Query", type="primary"):
                if question.strip():
                    with st.spinner("Processing query..."):
                        try:
                            result = st.session_state.llm_client.ask_question(
                                selected_doc["text_content"],
                                question,
                                model=st.session_state.selected_model
                            )
                            
                            st.markdown('<div class="answer-box">', unsafe_allow_html=True)
                            st.markdown("**Response:**")
                            st.write(result["answer"])
                            st.caption(f"Generated by {result['provider']} ({result['model']})")
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                        except Exception as e:
                            st.error(f"Error processing query: {str(e)}")
                else:
                    st.warning("Please enter a question before submitting.")
    
    # Tab 3: Batch Q&A Mode
    with tab3:
        st.subheader("Batch Question Processing Interface")
        
        if not st.session_state.documents:
            st.info("Please upload and process documents in the Document Upload tab before proceeding.")
        elif not llm_available:
            st.error("LLM client unavailable. Please ensure Ollama is running.")
        else:
            # Info about CSV optimization
            st.markdown("""
            <div class="info-box">
                <strong>CSV Output Format Optimization</strong><br>
                The system automatically formats LLM responses for optimal CSV compatibility:
                <ul>
                    <li>Single paragraph format (eliminates problematic line breaks)</li>
                    <li>Semicolon-delimited lists (instead of bullet points)</li>
                    <li>Concise, focused responses</li>
                    <li>Full field quoting for spreadsheet compatibility</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("Enter research questions (one per line) to process across all loaded documents:")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Multiple questions input
                batch_questions_input = st.text_area(
                    "Research Questions:",
                    value=st.session_state.batch_questions,
                    placeholder="What is the main research objective?\nWhat methodology was employed?\nWhat are the key findings?",
                    height=200,
                    help="Each line will be processed as a separate question"
                )
                
                # Update session state
                st.session_state.batch_questions = batch_questions_input
                
                # Parse questions
                questions = [q.strip() for q in batch_questions_input.split('\n') if q.strip()]
                
                if questions:
                    st.info(f"{len(questions)} question(s) will be processed for {len(st.session_state.documents)} document(s)")
                    st.caption(f"Total Q&A pairs to generate: {len(questions) * len(st.session_state.documents)}")
            
            with col2:
                st.markdown("**Question Templates**")
                
                if st.button("Research Analysis"):
                    st.session_state.batch_questions = """What is the main research question or objective?
What methodology was employed in this study?
What are the key findings and results?
What are the main conclusions drawn?
What limitations are acknowledged?"""
                    st.rerun()
                
                if st.button("Document Summary"):
                    st.session_state.batch_questions = """Provide a brief summary of this document
What are the main points discussed?
Who is the intended audience?
What recommendations or actions are proposed?"""
                    st.rerun()
                
                if st.button("Data Extraction"):
                    st.session_state.batch_questions = """What dates or time periods are referenced?
What numerical data or statistics are provided?
Who are the key individuals or organizations mentioned?
What geographic locations are referenced?"""
                    st.rerun()
                
                if st.button("Clear Input"):
                    st.session_state.batch_questions = ""
                    st.rerun()
            
            st.divider()
            
            # Process batch button
            if st.button("Process Batch Analysis", type="primary", disabled=len(questions) == 0):
                if questions:
                    with st.spinner(f"Processing {len(questions) * len(st.session_state.documents)} Q&A pairs..."):
                        try:
                            # Process all questions for all documents
                            results = st.session_state.batch_processor.process_multiple_documents_batch(
                                documents=st.session_state.documents,
                                questions=questions,
                                model=st.session_state.selected_model
                            )
                            
                            # Export to CSV
                            csv_path = st.session_state.batch_processor.export_to_csv(results)
                            
                            # Show success message
                            st.success(f"Successfully completed {len(results)} Q&A pairs")
                            
                            # Provide download button
                            with open(csv_path, 'rb') as f:
                                st.download_button(
                                    label="Download Results (CSV)",
                                    data=f,
                                    file_name=os.path.basename(csv_path),
                                    mime="text/csv",
                                    type="primary"
                                )
                            
                            # Show preview using pandas
                            st.markdown('<p class="section-header">Analysis Results Preview</p>', unsafe_allow_html=True)
                            
                            # Display summary statistics
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Total Q&A Pairs", len(results))
                            with col2:
                                success_count = sum(1 for r in results if r['status'] == 'success')
                                st.metric("Successful", success_count)
                            with col3:
                                error_count = sum(1 for r in results if r['status'] == 'error')
                                st.metric("Errors", error_count)
                            
                            # Load CSV into pandas for display
                            df = pd.read_csv(csv_path)
                            
                            # Show dataframe preview
                            st.write("**CSV Data Preview (First 10 Rows):**")
                            st.dataframe(
                                df.head(10),
                                use_container_width=True,
                                hide_index=True
                            )
                            
                            if len(df) > 10:
                                st.info(f"Displaying 10 of {len(df)} total rows. Download CSV file for complete results.")
                            
                            # Show sample answers in detail
                            st.write("**Detailed Response Preview:**")
                            
                            # Group by document for organized display
                            for doc_name in df['document_name'].unique()[:2]:  # Show first 2 documents
                                doc_results = df[df['document_name'] == doc_name]
                                
                                with st.expander(f"{doc_name} ({len(doc_results)} Q&A pairs)"):
                                    for idx, row in doc_results.head(3).iterrows():  # Show first 3 per doc
                                        st.markdown(f"**Question {row['question_number']}:** {row['question']}")
                                        
                                        if row['status'] == 'success':
                                            st.markdown('<div class="answer-box">', unsafe_allow_html=True)
                                            st.write(row['answer'])
                                            st.caption(f"Model: {row['model']}")
                                            st.markdown('</div>', unsafe_allow_html=True)
                                        else:
                                            st.error(f"Processing Error: {row['error']}")
                                        
                                        if idx < len(doc_results) - 1:
                                            st.divider()
                                    
                                    if len(doc_results) > 3:
                                        st.info(f"Displaying 3 of {len(doc_results)} Q&A pairs for this document.")
                            
                            # Usage guidelines
                            st.markdown("""
                            <div class="tips-section">
                                <strong>Guidelines for CSV Usage</strong>
                                <ul>
                                    <li><strong>Spreadsheet Applications:</strong> Open directly in Excel, Google Sheets, or LibreOffice Calc</li>
                                    <li><strong>Text Formatting:</strong> Enable "Wrap text" feature in the answer column for optimal readability</li>
                                    <li><strong>Column Management:</strong> Adjust answer column width to display complete responses</li>
                                    <li><strong>Data Filtering:</strong> Apply filters to sort by document name, status, or question number</li>
                                    <li><strong>Further Analysis:</strong> Responses are formatted as plain text, suitable for qualitative analysis tools</li>
                                    <li><strong>Citation:</strong> Include document name and question number when referencing specific responses</li>
                                </ul>
                            </div>
                            """, unsafe_allow_html=True)
                            
                        except Exception as e:
                            st.error(f"Error during batch processing: {str(e)}")
                else:
                    st.warning("Please enter at least one question before processing.")


if __name__ == "__main__":
    main()