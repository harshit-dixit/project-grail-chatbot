import os
import fitz  # PyMuPDF
import docx2txt
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import config
import logging

logger = logging.getLogger(__name__)

def load_documents_from_sops_dir():
    """Loads all documents from the SOP_DIR and returns a list of their texts."""
    documents_text = []
    sops_directory = config.SOP_DIR_PATH 
    logger.info(f"Looking for documents in: {os.path.abspath(sops_directory)}")
    if not os.path.isdir(sops_directory):
        logger.error(f"Directory '{sops_directory}' not found. Please create it and add your SOP documents.")
        return []

    for filename in os.listdir(sops_directory):
        file_path = os.path.join(sops_directory, filename)
        try:
            if filename.endswith(".pdf"):
                logger.info(f"Loading PDF: {filename} using PyMuPDF")
                text = ""
                try:
                    doc = fitz.open(file_path)
                    for page_num in range(len(doc)):
                        page = doc.load_page(page_num)
                        page_text = page.get_text("text") # "text" for plain text extraction
                        if page_text:
                            text += page_text
                    doc.close() # Important: close the document
                except Exception as e:
                    logger.error(f"Error processing PDF {filename} with PyMuPDF: {e}")
                    # Optionally, you might want to skip this file or handle the error differently
                
                if text:
                    documents_text.append({'name': filename, 'text': text})
                else:
                    logger.warning(f"Could not extract text from PDF: {filename} using PyMuPDF, or PDF was empty.")
            elif filename.endswith(".docx"):
                logger.info(f"Loading DOCX: {filename}")
                text = docx2txt.process(file_path)
                if text:
                    documents_text.append({'name': filename, 'text': text})
                else:
                    logger.warning(f"Could not extract text from DOCX: {filename} or DOCX was empty.")
            elif filename.endswith(".txt"):
                logger.info(f"Loading TXT: {filename}")
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                if text:
                    documents_text.append({'name': filename, 'text': text})
                else:
                    logger.warning(f"TXT file is empty: {filename}")
            # else: # Optional: handle other file types or ignore
            #     logger.info(f"Skipping unsupported file type: {filename}")
        except Exception as e:
            logger.error(f"Error loading document {filename}: {e}", exc_info=True)
    
    if not documents_text:
        logger.warning("No documents loaded. Please ensure your SOP documents are in the 'sops' directory and are in .txt, .pdf, or .docx format.")
    return documents_text

def get_text_chunks(documents_data):
    """Splits the text from loaded documents into manageable chunks."""
    if not documents_data:
        return []
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.TEXT_CHUNK_SIZE, 
        chunk_overlap=config.TEXT_CHUNK_OVERLAP,
        length_function=len
    )
    
    all_chunks = [] 
    for doc_data in documents_data: 
        doc_text = doc_data.get('text', '')
        if not isinstance(doc_text, str) or not doc_text.strip(): 
            logger.warning(f"Document '{doc_data.get('name', 'Unknown')}' has no valid text content or is empty. Skipping.")
            continue

        chunks_text_list = text_splitter.split_text(doc_text) 
        
        for i, chunk_content in enumerate(chunks_text_list):
            metadata = {
                'source': doc_data['name'], 
                'chunk_id': f"{doc_data['name']}_chunk_{i}"
            }
            document = Document(page_content=chunk_content, metadata=metadata)
            all_chunks.append(document)
    
    if not all_chunks:
        logger.warning("No text chunks were created. Ensure documents have extractable text.")
    else:
        logger.info(f"Created {len(all_chunks)} Document objects as chunks.")
    return all_chunks
