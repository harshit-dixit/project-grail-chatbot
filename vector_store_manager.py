import os
import pickle 
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from utils import get_text_chunks, load_documents_from_sops_dir 
from gemini_handler import load_api_key 
import traceback

VECTOR_STORE_DIR = "faiss_index"
VECTOR_STORE_PATH = os.path.join(VECTOR_STORE_DIR, "sop_index.faiss")
TEXT_CHUNKS_PATH = os.path.join(VECTOR_STORE_DIR, "text_chunks.pkl") 

def get_embeddings_model():
    try:
        load_api_key() 
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        return embeddings
    except Exception as e:
        print(f"Error initializing embeddings model: {e}")
        raise RuntimeError(f"Could not initialize embeddings model: {e}. Check API key and model name.")

def create_vector_store(text_chunks_data, force_recreate=False):
    if not text_chunks_data:
        print("No text chunks provided to create vector store.")
        return None

    if not os.path.exists(VECTOR_STORE_DIR):
        os.makedirs(VECTOR_STORE_DIR)
        print(f"Created directory: {VECTOR_STORE_DIR}")

    if os.path.exists(VECTOR_STORE_PATH) and os.path.exists(TEXT_CHUNKS_PATH) and not force_recreate:
        print(f"Loading existing vector store from {VECTOR_STORE_PATH}")
        try:
            embeddings = get_embeddings_model()
            vector_store = FAISS.load_local(VECTOR_STORE_DIR, embeddings, index_name="sop_index", allow_dangerous_deserialization=True)
            with open(TEXT_CHUNKS_PATH, 'rb') as f:
                stored_text_chunks = pickle.load(f)
            if len(stored_text_chunks) == vector_store.index.ntotal:
                print("Successfully loaded vector store and associated text chunks.")
                return vector_store, stored_text_chunks
            else:
                print("Mismatch between loaded vector store and text chunks. Recreating...")
        except Exception as e:
            print(f"Error loading existing vector store: {e}. Recreating...")
    
    print("Creating new vector store...")
    try:
        embeddings = get_embeddings_model()
        contents = [chunk['content'] for chunk in text_chunks_data]
        metadatas = [{'source': chunk['source'], 'chunk_id': chunk['chunk_id']} for chunk in text_chunks_data]
        
        vector_store = FAISS.from_texts(texts=contents, embedding=embeddings, metadatas=metadatas)
        vector_store.save_local(VECTOR_STORE_DIR, index_name="sop_index")
        with open(TEXT_CHUNKS_PATH, 'wb') as f:
            pickle.dump(text_chunks_data, f)
        print(f"Vector store created and saved to {VECTOR_STORE_PATH} and {TEXT_CHUNKS_PATH}")
        return vector_store, text_chunks_data
    except Exception as e:
        print(f"Error creating vector store: {e}")
        if os.path.exists(VECTOR_STORE_PATH):
            os.remove(VECTOR_STORE_PATH)
        if os.path.exists(TEXT_CHUNKS_PATH):
            os.remove(TEXT_CHUNKS_PATH)
        return None, None

def get_retriever(vector_store, search_type="similarity", k_results=5):
    """
    Creates a retriever from the given FAISS vector store.

    Args:
        vector_store: The FAISS vector store instance.
        search_type (str): The type of search to perform ('similarity', 'mmr', etc.).
        k_results (int): The number of top results to retrieve.

    Returns:
        A LangChain retriever object, or None if the vector store is invalid.
    """
    if not vector_store:
        print("Error: Vector store is None, cannot create retriever.")
        return None
    try:
        retriever = vector_store.as_retriever(search_type=search_type, search_kwargs={"k": k_results})
        print(f"Retriever created successfully. Search type: {search_type}, k: {k_results}")
        return retriever
    except Exception as e:
        print(f"Error creating retriever: {e}")
        traceback.print_exc()
        return None

def get_similar_docs(query, vector_store, k=5):
    if not vector_store:
        print("Vector store is not available.")
        return []
    try:
        similar_docs = vector_store.similarity_search(query, k=k)
        return similar_docs 
    except Exception as e:
        print(f"Error during similarity search: {e}")
        return []

if __name__ == '__main__':
    print("Testing vector_store_manager.py...")
    SOP_TEST_DIR = "sops"
    if not os.path.exists(SOP_TEST_DIR):
        os.makedirs(SOP_TEST_DIR)
    if not os.path.exists(os.path.join(SOP_TEST_DIR, "test_sop.txt")):
        with open(os.path.join(SOP_TEST_DIR, "test_sop.txt"), "w") as f:
            f.write("This is a test SOP document. It describes how to test the system. First, do A. Second, do B. Finally, do C.")
        print(f"Created dummy '{SOP_TEST_DIR}/test_sop.txt' for testing.")

    try:
        print("\nStep 1: Loading documents...")
        raw_docs_data = load_documents_from_sops_dir() 
        if not raw_docs_data:
            print("No documents loaded. Ensure 'sops' directory exists and contains files.")
        else:
            print(f"Loaded {len(raw_docs_data)} document(s).")

            print("\nStep 2: Getting text chunks...")
            all_text_chunks = get_text_chunks(raw_docs_data) 
            if not all_text_chunks:
                print("No text chunks created. Ensure documents have content.")
            else:
                print(f"Created {len(all_text_chunks)} text chunks.")
                print("\nStep 3: Creating/Loading vector store...")
                vs, stored_chunks = create_vector_store(all_text_chunks, force_recreate=False) 
                if vs and stored_chunks:
                    print("Vector store ready.")
                    print(f"Vector store has {vs.index.ntotal} embeddings.")
                    print(f"Number of stored text chunks: {len(stored_chunks)}.")

                    print("\nStep 4: Testing similarity search...")
                    query1 = "how to test the system"
                    similar_documents = get_similar_docs(query1, vs, k=2)
                    if similar_documents:
                        print(f"\nFound {len(similar_documents)} docs for query: '{query1}'")
                        for i, doc in enumerate(similar_documents):
                            print(f"  Doc {i+1} (Source: {doc.metadata.get('source')}, Chunk ID: {doc.metadata.get('chunk_id')})")
                            print(f"    Content snippet: {doc.page_content[:150]}...")
                    else:
                        print(f"No similar documents found for query: '{query1}'")
                    
                    query2 = "information about safety procedures"
                    similar_documents_2 = get_similar_docs(query2, vs, k=2)
                    if similar_documents_2:
                        print(f"\nFound {len(similar_documents_2)} docs for query: '{query2}'")
                        for i, doc in enumerate(similar_documents_2):
                            print(f"  Doc {i+1} (Source: {doc.metadata.get('source')}, Chunk ID: {doc.metadata.get('chunk_id')})")
                            print(f"    Content snippet: {doc.page_content[:150]}...")
                    else:
                        print(f"No similar documents found for query: '{query2}'")
                else:
                    print("Failed to create or load vector store.")

    except RuntimeError as re:
        print(f"Runtime Error: {re}")
        print("Please ensure your GOOGLE_API_KEY is correctly set in the .env file in the project root.")
    except Exception as e:
        print(f"An unexpected error occurred during testing: {e}")
