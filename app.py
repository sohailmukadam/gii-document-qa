import streamlit as st
import os
import tempfile
import pandas as pd
from typing import Dict, Any, List
from document_processor import DocumentProcessor
from llm_client import LLMClient
from batch_qa_processor import BatchQAProcessor

# Page configuration
st.set_page_config(
    page_title="Document Q&A System",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    """Initialize LLM client and batch processor."""
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
    
    # Create a temp directory for uploaded files
    temp_dir = tempfile.mkdtemp()
    progress_bar = st.progress(0)
    status_text = st.empty()
    for idx, uploaded_file in enumerate(uploaded_files):
        status_text.text(f"Processing {idx + 1}/{len(uploaded_files)}: {uploaded_file.name}")
        
        # Save with original filename in temp directory
        file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getvalue())
        try:
            # Process the document (will use cache if available)
            document_data = doc_processor.process_document(file_path)
            processed_docs.append(document_data)
            
            # Clean up this file
            os.unlink(file_path)
        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {str(e)}")
            if os.path.exists(file_path):
                os.unlink(file_path)
        progress_bar.progress((idx + 1) / len(uploaded_files))
    status_text.text("All documents processed successfully")
    progress_bar.empty()
    status_text.empty()
    
    # Clean up temp directory
    try:
        os.rmdir(temp_dir)
    except:
        pass
    return processed_docs

def main():
    """Main Streamlit application."""
    
    # Header
    st.title("Document Q&A System")
    st.subheader("Automated Question-Answering for Dataset Generation")
    
    # Sidebar
    with st.sidebar:
        st.header("System Configuration")
 
        # Initialize clients
        llm_available = initialize_clients()
        if llm_available:
            st.success("Status: Online")
            
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
            st.error("Status: Offline")
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
                        st.success("Cached")
            if st.button("Clear All Documents", type="secondary"):
                st.session_state.documents = []
                st.rerun()
    
    # Main content tabs
    tab1, tab2 = st.tabs(["Document Upload", "Batch Processing"])
    
    # Tab 1: Upload Documents
    with tab1:
        st.subheader("Document Upload Interface")
        uploaded_files = st.file_uploader(
            "Select PDF Documents",
            type=['pdf'],
            accept_multiple_files=True,
            help="Upload one or more PDF documents. Previously processed documents will be loaded from cache."
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
    
    # Tab 2: Batch Q&A Mode
    with tab2:
        st.subheader("Batch Question Processing Interface")
        if not st.session_state.documents:
            st.info("Please upload and process documents in the Document Upload tab before proceeding.")
        elif not llm_available:
            st.error("LLM client unavailable. Please ensure Ollama is running.")
        else:
            st.write("Enter questions (one per line) to process across all loaded documents:")
            batch_questions_input = st.text_area(
                "Questions:",
                value=st.session_state.batch_questions,
                placeholder="What is the main research objective?\nWhat methodology was employed?\nWhat are the key findings?",
                help="Each line will be processed as a separate question"
            )
            
            # Update session state
            st.session_state.batch_questions = batch_questions_input
            
            # Parse questions
            questions = [q.strip() for q in batch_questions_input.split('\n') if q.strip()]
            if questions:
                st.info(f"{len(questions)} question(s) will be processed for {len(st.session_state.documents)} document(s)")
                st.caption(f"Total Q&A pairs to generate: {len(questions) * len(st.session_state.documents)}")
            st.divider()
            
            # Process batch button
            if st.button("Process", type="primary", disabled=len(questions) == 0):
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
                            st.subheader("Results Preview")
                            
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
                                        st.write(f"**Question {row['question_number']}:** {row['question']}")
                                        if row['status'] == 'success':
                                            st.success("Answer:")
                                            st.write(row['answer'])
                                            st.caption(f"Model: {row['model']}")
                                        else:
                                            st.error(f"Processing Error: {row['error']}")
                                        if idx < len(doc_results) - 1:
                                            st.divider()
                                    if len(doc_results) > 3:
                                        st.info(f"Displaying 3 of {len(doc_results)} Q&A pairs for this document.")
                        except Exception as e:
                            st.error(f"Error during batch processing: {str(e)}")
                else:
                    st.warning("Please enter at least one question before processing.")


if __name__ == "__main__":
    main()