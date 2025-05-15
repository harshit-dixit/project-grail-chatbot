import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback
import logging
import config

# Project-specific modules
from utils import load_documents_from_sops_dir, get_text_chunks
from vector_store_manager import create_vector_store, get_retriever
from gemini_handler import get_llm, get_conversational_chain, load_api_key

app = Flask(__name__)
CORS(app) # Enable CORS for all routes, allowing React frontend to call

# --- Logging Setup ---
log_level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO) # Get log level from config, default to INFO
logging.basicConfig(level=log_level, 
                    format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
                    handlers=[
                        logging.FileHandler(config.LOG_FILE_NAME), 
                        logging.StreamHandler() # To also log to console
                    ])
logger = logging.getLogger(__name__)
# ---

# Global state (in-memory, simple approach for now)
# In a production app, you might use a more robust state management or database
app_state = {
    "api_key_loaded": False,
    "sops_processed": False,
    "vector_store": None,
    "qa_chain": None,
    "processed_docs_count": 0,
    "processed_chunks_count": 0,
    "error_message": None
}

def initialize_app():
    """Initializes API key and basic configurations."""
    try:
        load_api_key() # This will raise ValueError if key is not found/set
        app_state["api_key_loaded"] = True
        app_state["error_message"] = None
        logger.info("Application initialized: API key loaded successfully.")
        # Initialize LLM and QA chain components that don't depend on documents yet
        llm = get_llm()
        if llm:
            # QA chain might be better initialized after vector store is ready
            # For now, let's assume it can be partially set up or fully after SOPs
            pass # app_state["qa_chain"] = get_conversational_chain(llm) if needed standalone
            logger.info("LLM initialized successfully.")
        else:
            app_state["error_message"] = "Failed to initialize LLM. Check API key and Gemini setup."
            app_state["api_key_loaded"] = False # if LLM fails, likely key issue
            logger.error(f"Failed to initialize LLM. API Key Loaded: {app_state['api_key_loaded']}. Error: {app_state['error_message']}")
            return False
        return True
    except ValueError as e:
        app_state["api_key_loaded"] = False
        app_state["error_message"] = str(e)
        logger.error(f"API Key Initialization Error: {e}")
        return False
    except Exception as e:
        app_state["api_key_loaded"] = False
        app_state["error_message"] = f"An unexpected error occurred during initialization: {str(e)}"
        logger.critical(f"Unexpected Initialization Error: {e}", exc_info=True)
        return False

@app.route('/api/status', methods=['GET'])
def get_status():
    """Returns the current status of the backend processing."""
    return jsonify({
        "api_key_loaded": app_state["api_key_loaded"],
        "sops_processed": app_state["sops_processed"],
        "processed_docs_count": app_state["processed_docs_count"],
        "processed_chunks_count": app_state["processed_chunks_count"],
        "error_message": app_state["error_message"]
    })

@app.route('/api/process_sops', methods=['POST'])
def process_sops():
    """Loads SOP documents, creates vector store, and initializes QA chain."""
    if not app_state["api_key_loaded"]:
        logger.warning("process_sops called but API key not loaded.")
        return jsonify({"success": False, "message": "API key not loaded. Please check backend logs."}), 500

    try:
        logger.info("'/api/process_sops' endpoint called. Starting SOP processing...")
        app_state["sops_processed"] = False # Reset status before processing
        documents_data = load_documents_from_sops_dir()
        if not documents_data:
            app_state["error_message"] = "No documents found in 'sops' directory or failed to load."
            logger.warning(f"SOP Processing: {app_state['error_message']}")
            return jsonify({"success": False, "message": app_state["error_message"]}), 400
        
        app_state["processed_docs_count"] = len(documents_data)
        logger.info(f"SOP Processing: Loaded {app_state['processed_docs_count']} documents.")
        # Correctly call get_text_chunks with the list of document data
        all_text_chunks = get_text_chunks(documents_data)
        
        app_state["processed_chunks_count"] = len(all_text_chunks)
        logger.info(f"SOP Processing: Created {app_state['processed_chunks_count']} text chunks.")
        if not all_text_chunks:
            app_state["error_message"] = "Documents were found but produced no text chunks for processing."
            logger.warning(f"SOP Processing: {app_state['error_message']}")
            return jsonify({"success": False, "message": app_state["error_message"]}), 400

        # Unpack the result from create_vector_store
        vector_store_object, stored_text_chunks_data = create_vector_store(all_text_chunks)
        app_state["vector_store"] = vector_store_object
        # Optionally, store stored_text_chunks_data if needed elsewhere in app_state
        # app_state["stored_text_chunks"] = stored_text_chunks_data

        if not app_state["vector_store"]:
            app_state["error_message"] = "Failed to create or retrieve vector store from chunks."
            logger.error(f"SOP Processing: {app_state['error_message']}")
            return jsonify({"success": False, "message": app_state["error_message"]}), 500

        llm = get_llm()
        if not llm:
            app_state["error_message"] = "Failed to get LLM for QA chain."
            logger.error(f"SOP Processing: {app_state['error_message']}")
            return jsonify({"success": False, "message": app_state["error_message"]}), 500
        
        # Ensure the retriever is correctly created from the vector store
        retriever = get_retriever(app_state["vector_store"])
        if not retriever:
            app_state["error_message"] = "Failed to create retriever from vector store."
            logger.error(f"SOP Processing: {app_state['error_message']}")
            return jsonify({"success": False, "message": app_state["error_message"]}), 500

        app_state["qa_chain"] = get_conversational_chain(llm, retriever)
        if not app_state["qa_chain"]:
            app_state["error_message"] = "Failed to create conversational QA chain."
            logger.error(f"SOP Processing: {app_state['error_message']}")
            return jsonify({"success": False, "message": app_state["error_message"]}), 500

        app_state["sops_processed"] = True
        app_state["error_message"] = None # Clear previous errors
        logger.info("SOPs processed successfully.")
        return jsonify({
            "success": True, 
            "message": "SOPs processed successfully.",
            "processed_docs_count": app_state["processed_docs_count"],
            "processed_chunks_count": app_state["processed_chunks_count"]
        })

    except Exception as e:
        app_state["sops_processed"] = False
        app_state["error_message"] = f"Error processing SOPs: {str(e)}"
        logger.error(f"Error in /api/process_sops: {e}", exc_info=True)
        return jsonify({"success": False, "message": app_state["error_message"]}), 500

@app.route('/api/ask', methods=['POST'])
def ask_question():
    """Receives a question, gets context, and returns the answer."""
    if not app_state["sops_processed"] or not app_state["qa_chain"]:
        logger.warning("'/api/ask' called but SOPs not processed or QA chain not initialized.")
        return jsonify({"answer": "SOPs not processed yet or QA chain not initialized. Please process SOPs first."}), 400

    data = request.get_json()
    question = data.get('question')
    logger.info(f"Received question: '{question}'")
    if not question:
        logger.warning("No question provided in /api/ask request.")
        return jsonify({"error": "No question provided."}), 400

    try:
        # The get_conversational_chain now directly uses the retriever passed to it.
        # The chain itself handles the document retrieval and response generation.
        # RetrievalQA chain expects the user's question under the 'query' key.
        result = app_state["qa_chain"]({"query": question, "chat_history": []}) # Corrected key to 'query'
        answer = result.get("result", "No answer found.") # RetrievalQA returns the answer in 'result'
        
        # Optional: include source documents if available and desired
        source_documents_for_log = []
        if "source_documents" in result and result["source_documents"]:
            for doc in result["source_documents"]:
                source_info_log = f"Source: {doc.metadata.get('file_name', 'Unknown')}, Page: {doc.metadata.get('page', 'N/A')}, Snippet: {doc.page_content[:75]}..."
                source_documents_for_log.append(source_info_log)
            logger.info(f"Retrieved {len(source_documents_for_log)} source documents for question: '{question}'. Details: {'; '.join(source_documents_for_log)}")
        else:
            logger.info(f"No source documents retrieved for question: '{question}'.")

        source_documents_for_response = []
        if "source_documents" in result and result["source_documents"]:
            for doc in result["source_documents"]:
                source_info = {"content": doc.page_content[:250] + "... (truncated)", "metadata": doc.metadata} 
                source_documents_for_response.append(source_info)
        
        logger.info(f"LLM Answer: '{answer[:100]}...'" ) # Log a snippet of the answer
        return jsonify({"answer": answer, "source_documents": source_documents_for_response})
    
    except Exception as e:
        error_message = f"Error processing question: {str(e)}"
        logger.error(f"Error in /api/ask: {e}", exc_info=True)
        return jsonify({"error": error_message}), 500

if __name__ == '__main__':
    # Ensure the API key is loaded at startup if it's not already handled by get_llm or similar.
    # This might be redundant if get_llm() already calls load_api_key().
    try:
        load_api_key()
        app_state["api_key_loaded"] = True
        logger.info("Flask app starting: API key loaded.")
    except ValueError as ve:
        app_state["api_key_loaded"] = False
        app_state["error_message"] = str(ve)
        logger.error(f"Flask app startup error: {str(ve)}")
    except Exception as ex:
        app_state["api_key_loaded"] = False
        app_state["error_message"] = f"An unexpected error occurred during API key loading at startup: {str(ex)}"
        logger.critical(f"Flask app startup - unexpected error during API key loading: {ex}", exc_info=True)

    # Call initialize_app to set up LLM etc. This was missing from direct __main__ execution path.
    if not initialize_app():
        logger.warning("Application initialization failed in __main__. Check logs for details. App will still run but may not be functional.")

    logger.info("Starting Flask app on host 0.0.0.0, port 5001")
    app.run(host='0.0.0.0', port=5001, debug=True)
