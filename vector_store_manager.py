import os
import pickle 
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document

from utils import get_text_chunks, load_documents_from_sops_dir 
from gemini_handler import get_gemini_api_key_for_embeddings 
import traceback
import logging 
import config 

logger = logging.getLogger(__name__) 

VECTOR_STORE_DIR = "faiss_index"
VECTOR_STORE_PATH = os.path.join(VECTOR_STORE_DIR, "sop_index.faiss")
TEXT_CHUNKS_PATH = os.path.join(VECTOR_STORE_DIR, "text_chunks.pkl") 

def get_embeddings_model():
    try:
        api_key = get_gemini_api_key_for_embeddings()
        if not api_key:
            # This should ideally be caught by load_api_key() in gemini_handler.py,
            # but as an additional safeguard here.
            raise ValueError("GEMINI_API_KEY not found in environment variables after attempting to load it.")
        
        embeddings = GoogleGenerativeAIEmbeddings(
            model=config.EMBEDDING_MODEL_NAME, 
            google_api_key=api_key  # Explicitly pass the API key
        )
        return embeddings
    except Exception as e:
        logger.error(f"Error initializing embeddings model: {e}", exc_info=True) 
        # If the exception is already a ValueError or RuntimeError, re-raise it directly
        # to preserve its specific type, otherwise wrap it in a generic RuntimeError.
        if isinstance(e, (ValueError, RuntimeError)):
            raise
        raise RuntimeError(f"Could not initialize embeddings model: {e}. Check API key and model name.")

def create_vector_store(text_chunks_data, force_recreate=False):
    if not text_chunks_data:
        logger.warning("No text chunks (Document objects) provided to create vector store.") 
        return None, None

    if not os.path.exists(VECTOR_STORE_DIR):
        os.makedirs(VECTOR_STORE_DIR)
        logger.info(f"Created directory: {VECTOR_STORE_DIR}") 

    if os.path.exists(VECTOR_STORE_PATH) and os.path.exists(TEXT_CHUNKS_PATH) and not force_recreate:
        logger.info(f"Loading existing vector store from {VECTOR_STORE_PATH}") 
        try:
            embeddings = get_embeddings_model()
            vector_store = FAISS.load_local(VECTOR_STORE_DIR, embeddings, index_name="sop_index", allow_dangerous_deserialization=True)
            with open(TEXT_CHUNKS_PATH, 'rb') as f:
                stored_text_chunks = pickle.load(f)
            
            # Validate the loaded chunks
            if not isinstance(stored_text_chunks, list) or (stored_text_chunks and not all(isinstance(doc, Document) for doc in stored_text_chunks)):
                 logger.warning("Stored text_chunks.pkl does not contain a valid list of Document objects. Recreating...")
                 raise FileNotFoundError("Invalid format in text_chunks.pkl. Expected list of Document objects.") # Force recreation

            if vector_store.index and hasattr(vector_store.index, 'ntotal') and len(stored_text_chunks) == vector_store.index.ntotal:
                logger.info("Successfully loaded vector store and associated Document objects.") 
                return vector_store, stored_text_chunks
            else:
                logger.warning("Mismatch between loaded vector store index and stored Document objects, or index is empty. Recreating...") 
        except Exception as e:
            logger.error(f"Error loading existing vector store or validating stored chunks: {e}. Recreating...", exc_info=True) 
    
    logger.info("Creating new vector store from Document objects...") 
    try:
        embeddings = get_embeddings_model()
        
        vector_store = FAISS.from_documents(documents=text_chunks_data, embedding=embeddings)
        
        vector_store.save_local(VECTOR_STORE_DIR, index_name="sop_index")
        
        with open(TEXT_CHUNKS_PATH, 'wb') as f:
            pickle.dump(text_chunks_data, f) 
        logger.info(f"Vector store created from Document objects and saved to {VECTOR_STORE_PATH} and {TEXT_CHUNKS_PATH}") 
        return vector_store, text_chunks_data
    except Exception as e:
        logger.error(f"Error creating vector store: {e}", exc_info=True) 
        if os.path.exists(VECTOR_STORE_PATH):
            try: os.remove(VECTOR_STORE_PATH)
            except OSError as ose_remove_faiss: logger.error(f"Error removing stale FAISS index {VECTOR_STORE_PATH}: {ose_remove_faiss}")
        if os.path.exists(TEXT_CHUNKS_PATH):
            try: os.remove(TEXT_CHUNKS_PATH)
            except OSError as ose_remove_pkl: logger.error(f"Error removing stale pickle file {TEXT_CHUNKS_PATH}: {ose_remove_pkl}")
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
        logger.error("Vector store is None, cannot create retriever.") 
        return None
    try:
        retriever = vector_store.as_retriever(search_type=search_type, search_kwargs={"k": k_results})
        logger.info(f"Retriever created successfully. Search type: {search_type}, k: {k_results}") 
        return retriever
    except Exception as e:
        logger.error(f"Error creating retriever: {e}", exc_info=True) 
        return None

def get_similar_docs(query, vector_store, k=5):
    if not vector_store:
        logger.warning("Vector store is not available for similarity search.") 
        return []
    try:
        similar_docs = vector_store.similarity_search(query, k=k)
        return similar_docs 
    except Exception as e:
        logger.error(f"Error during similarity search: {e}", exc_info=True) 
        return []

if __name__ == '__main__':
    # Setup basic logging for the test
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    logger.info("Testing vector_store_manager.py...")
    SOP_TEST_DIR = config.SOP_DIR_PATH 
    if not os.path.exists(SOP_TEST_DIR):
        os.makedirs(SOP_TEST_DIR)
    if not os.path.exists(os.path.join(SOP_TEST_DIR, "test_sop.txt")):
        with open(os.path.join(SOP_TEST_DIR, "test_sop.txt"), "w") as f:
            f.write("This is a test SOP document. It describes how to test the system. First, do A. Second, do B. Finally, do C.")
        logger.info(f"Created dummy '{os.path.join(SOP_TEST_DIR, 'test_sop.txt')}' for testing.")

    try:
        logger.info("\nStep 1: Loading documents...")
        raw_docs_data = load_documents_from_sops_dir() 
        if not raw_docs_data:
            logger.warning("No documents loaded. Ensure 'sops' directory exists and contains files.")
        else:
            logger.info(f"Loaded {len(raw_docs_data)} document(s).")

            logger.info("\nStep 2: Getting text chunks...")
            all_text_chunks = get_text_chunks(raw_docs_data) 
            if not all_text_chunks:
                logger.warning("No text chunks created. Ensure documents have content.")
            else:
                logger.info(f"Created {len(all_text_chunks)} text chunks.")
                logger.info("\nStep 3: Creating/Loading vector store...")
                vs, stored_chunks = create_vector_store(all_text_chunks, force_recreate=False) 
                if vs and stored_chunks:
                    logger.info("Vector store ready.")
                    logger.info(f"Vector store has {vs.index.ntotal} embeddings.")
                    logger.info(f"Number of stored text chunks: {len(stored_chunks)}.")

                    logger.info("\nStep 4: Testing similarity search...")
                    query1 = "how to test the system"
                    similar_documents = get_similar_docs(query1, vs, k=2)
                    if similar_documents:
                        logger.info(f"\nFound {len(similar_documents)} docs for query: '{query1}'")
                        for i, doc in enumerate(similar_documents):
                            logger.info(f"  Doc {i+1} (Source: {doc.metadata.get('source')}, Chunk ID: {doc.metadata.get('chunk_id')})")
                            logger.info(f"    Content snippet: {doc.page_content[:150]}...")
                    else:
                        logger.warning(f"No similar documents found for query: '{query1}'")
                    
                    query2 = "information about safety procedures"
                    similar_documents_2 = get_similar_docs(query2, vs, k=2)
                    if similar_documents_2:
                        logger.info(f"\nFound {len(similar_documents_2)} docs for query: '{query2}'")
                        for i, doc in enumerate(similar_documents_2):
                            logger.info(f"  Doc {i+1} (Source: {doc.metadata.get('source')}, Chunk ID: {doc.metadata.get('chunk_id')})")
                            logger.info(f"    Content snippet: {doc.page_content[:150]}...")
                    else:
                        logger.warning(f"No similar documents found for query: '{query2}'")
                else:
                    logger.error("Failed to create or load vector store.")

    except RuntimeError as re:
        logger.error(f"Runtime Error: {re}", exc_info=True)
        logger.error("Please ensure your GEMINI_API_KEY is correctly set in the .env file in the project root.") 
    except Exception as e:
        logger.error(f"An unexpected error occurred during testing: {e}", exc_info=True)
