import os
from PyPDF2 import PdfReader
import docx2txt
from langchain.text_splitter import RecursiveCharacterTextSplitter
import config

def load_documents_from_sops_dir():
    """Loads all documents from the SOP_DIR and returns a list of their texts."""
    documents_text = []
    sops_directory = config.SOP_DIR_PATH 
    print(f"Looking for documents in: {os.path.abspath(sops_directory)}")
    if not os.path.isdir(sops_directory):
        print(f"Error: Directory '{sops_directory}' not found. Please create it and add your SOP documents.")
        return []

    for filename in os.listdir(sops_directory):
        file_path = os.path.join(sops_directory, filename)
        try:
            if filename.endswith(".pdf"):
                print(f"Loading PDF: {filename}")
                reader = PdfReader(file_path)
                text = ""
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text
                if text:
                    documents_text.append({'name': filename, 'text': text})
                else:
                    print(f"Warning: Could not extract text from PDF: {filename}")
            elif filename.endswith(".docx"):
                print(f"Loading DOCX: {filename}")
                text = docx2txt.process(file_path)
                if text:
                    documents_text.append({'name': filename, 'text': text})
                else:
                    print(f"Warning: Could not extract text from DOCX: {filename}")
            elif filename.endswith(".txt"):
                print(f"Loading TXT: {filename}")
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                if text:
                    documents_text.append({'name': filename, 'text': text})
                else:
                    print(f"Warning: TXT file is empty: {filename}")
            # else: # Optional: handle other file types or ignore
            #     print(f"Skipping unsupported file type: {filename}")
        except Exception as e:
            print(f"Error loading document {filename}: {e}")
    
    if not documents_text:
        print("No documents loaded. Please ensure your SOP documents are in the 'sops' directory and are in .txt, .pdf, or .docx format.")
    return documents_text

def get_text_chunks(documents_data):
    """Splits the text from loaded documents into manageable chunks."""
    if not documents_data:
        return []
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200,
        length_function=len
    )
    
    all_chunks = []
    for doc_data in documents_data:
        chunks = text_splitter.split_text(doc_data['text'])
        # Storing source document name with each chunk for potential future reference
        for i, chunk in enumerate(chunks):
            all_chunks.append({'source': doc_data['name'], 'content': chunk, 'chunk_id': f"{doc_data['name']}_chunk_{i}"})
    
    if not all_chunks:
        print("No text chunks were created. Ensure documents have extractable text.")
    else:
        print(f"Created {len(all_chunks)} text chunks.")
    return all_chunks

# Example usage (for testing purposes, can be removed later)
if __name__ == '__main__':
    # To test, create a 'sops' directory in the same location as utils.py
    # and add some .txt, .pdf, or .docx files.
    
    # Create a dummy sops directory and files for testing if they don't exist
    sops_test_dir = config.SOP_DIR_PATH
    if not os.path.exists(sops_test_dir):
        os.makedirs(sops_test_dir)
        with open(os.path.join(sops_test_dir, "sample.txt"), "w") as f:
            f.write("This is a sample text document for testing the SOP chatbot utility functions. It contains multiple sentences.")
        # You might need to manually add a sample.pdf and sample.docx for full testing
        print(f"Created dummy '{sops_test_dir}' directory and 'sample.txt'. Add PDF/DOCX files for more tests.")

    loaded_docs = load_documents_from_sops_dir()
    if loaded_docs:
        print(f"\nSuccessfully loaded {len(loaded_docs)} documents:")
        for doc in loaded_docs:
            print(f"- {doc['name']} (length: {len(doc['text'])})")
        
        chunks = get_text_chunks(loaded_docs)
        if chunks:
            print(f"\nSuccessfully created {len(chunks)} chunks.")
            # print("First few chunks:")
            # for i, chunk_data in enumerate(chunks[:2]):
            #     print(f"  Chunk {i+1} (from {chunk_data['source']}):\n    {chunk_data['content'][:100]}...\n")
    else:
        print("\nNo documents were loaded. Please check the 'sops' directory and file formats.")
