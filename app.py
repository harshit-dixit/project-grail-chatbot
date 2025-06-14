import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback
import logging
import config
from langchain_core.documents import Document
from werkzeug.utils import secure_filename

# Project-specific modules
from utils import load_documents_from_sops_dir, get_text_chunks
from vector_store_manager import create_vector_store, get_retriever
from gemini_handler import get_llm, get_conversational_chain

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
        # get_llm() will now handle necessary credential/config loading internally.
        # We'll consider api_key_loaded to be true if get_llm() succeeds.
        app_state["api_key_loaded"] = False # Assume not loaded until LLM is confirmed
        llm = get_llm()
        if llm:
            app_state["api_key_loaded"] = True
        app_state["error_message"] = None
        # LLM initialization is already attempted above to set api_key_loaded.
        if app_state["api_key_loaded"]:
            logger.info("LLM initialized successfully (implies API/config loaded).")
            # QA chain might be better initialized after vector store is ready
            # For now, let's assume it can be partially set up or fully after SOPs
        else:
            # Error message would have been set by get_llm() or CustomGenAILLM if it failed
            if not app_state["error_message"]:
                 app_state["error_message"] = "Failed to initialize LLM. Check logs for details."
            logger.error(f"LLM initialization failed. Error: {app_state['error_message']}")
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
        return jsonify({"success": False, "message": "API key not loaded. Please check backend logs.", "docs_count": 0, "chunks_count": 0}), 500

    try:
        logger.info("'/api/process_sops' endpoint called. Attempting to refresh knowledge base.")
        
        # Explicitly clear old state to ensure a full refresh
        app_state["vector_store"] = None
        app_state["qa_chain"] = None
        app_state["sops_processed"] = False
        app_state["processed_docs_count"] = 0
        app_state["processed_chunks_count"] = 0
        app_state["error_message"] = None
        logger.info("Previous application state for SOPs cleared.")

        documents_data = load_documents_from_sops_dir() # This function should log files it finds/doesn't find
        
        if not documents_data:
            app_state["error_message"] = "No documents found in 'sops' directory or failed to load any."
            logger.warning(app_state["error_message"])
            return jsonify({"success": False, "message": app_state["error_message"], "docs_count": 0, "chunks_count": 0}), 200

        logger.info(f"Successfully loaded {len(documents_data)} documents from '{config.SOP_DIR_PATH}'.")
        app_state["processed_docs_count"] = len(documents_data)

        text_chunks_with_source = get_text_chunks(documents_data)
        if not text_chunks_with_source:
            app_state["error_message"] = "Failed to create text chunks from the loaded documents."
            logger.warning(app_state["error_message"])
            return jsonify({"success": False, "message": app_state["error_message"], "docs_count": app_state["processed_docs_count"], "chunks_count": 0}), 200

        # text_chunks_with_source is already a list of Document objects, no need to convert
        app_state["processed_chunks_count"] = len(text_chunks_with_source)
        logger.info(f"Successfully created {app_state['processed_chunks_count']} text chunks.")

        # Pass the Document objects directly to create_vector_store
        vector_store_object, returned_chunks_data = create_vector_store(text_chunks_with_source, force_recreate=True) 
        app_state["vector_store"] = vector_store_object
        
        if not app_state["vector_store"]:
            app_state["error_message"] = "Failed to create vector store."
            logger.error(app_state["error_message"])
            return jsonify({"success": False, "message": app_state["error_message"], "docs_count": app_state["processed_docs_count"], "chunks_count": app_state["processed_chunks_count"]}), 500
        logger.info("Vector store created successfully.")

        llm = get_llm() # Ensure LLM is available
        if not llm:
            app_state["error_message"] = "LLM not available. Cannot create QA chain."
            logger.error(app_state["error_message"])
            return jsonify({"success": False, "message": app_state["error_message"], "docs_count": app_state["processed_docs_count"], "chunks_count": app_state["processed_chunks_count"]}), 500
        logger.info("LLM obtained successfully.")

        retriever = get_retriever(app_state["vector_store"])
        app_state["qa_chain"] = get_conversational_chain(llm, retriever)
        if not app_state["qa_chain"]:
            app_state["error_message"] = "Failed to create conversational QA chain."
            logger.error(app_state["error_message"])
            return jsonify({"success": False, "message": app_state["error_message"], "docs_count": app_state["processed_docs_count"], "chunks_count": app_state["processed_chunks_count"]}), 500
        logger.info("Conversational QA chain created successfully.")

        app_state["sops_processed"] = True
        app_state["error_message"] = None 
        logger.info(f"SOP processing complete. Docs: {app_state['processed_docs_count']}, Chunks: {app_state['processed_chunks_count']}. QA chain is ready.")
        return jsonify({
            "success": True, 
            "message": "SOPs processed successfully.",
            "docs_count": app_state["processed_docs_count"],
            "chunks_count": app_state["processed_chunks_count"]
        }), 200
    
    except Exception as e:
        app_state["sops_processed"] = False # Ensure it's marked as not processed on any error
        app_state["error_message"] = f"Error processing SOPs: {str(e)}"
        logger.error(f"Error in /api/process_sops: {e}", exc_info=True)
        # Return counts as 0 if error occurred before they were determined
        doc_count = app_state.get("processed_docs_count", 0)
        chunk_count = app_state.get("processed_chunks_count", 0)
        return jsonify({"success": False, "message": app_state["error_message"], "docs_count": doc_count, "chunks_count": chunk_count}), 500

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
        result = app_state["qa_chain"].invoke({"query": question, "chat_history": []}) # Use invoke for newer Langchain
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

@app.route('/api/list_sops', methods=['GET'])
def list_sops():
    """Lists SOP files currently in the SOPs directory."""
    sops_dir = config.SOP_DIR_PATH
    if not os.path.exists(sops_dir) or not os.path.isdir(sops_dir):
        logger.warning(f"SOPs directory '{sops_dir}' not found.")
        return jsonify({"sops": [], "message": "SOPs directory not found."}), 404
    try:
        sop_files = [f for f in os.listdir(sops_dir) if os.path.isfile(os.path.join(sops_dir, f))]
        logger.info(f"Found {len(sop_files)} SOP files in '{sops_dir}'.")
        return jsonify({"sops": sop_files, "count": len(sop_files)}), 200
    except Exception as e:
        logger.error(f"Error listing SOP files: {e}", exc_info=True)
        return jsonify({"sops": [], "message": f"Error listing SOP files: {str(e)}"}), 500

@app.route('/api/upload_sop', methods=['POST'])
def upload_sop():
    """Handles SOP file uploads."""
    sops_dir = config.SOP_DIR_PATH
    if not os.path.exists(sops_dir):
        try:
            os.makedirs(sops_dir)
            logger.info(f"SOPs directory '{sops_dir}' created.")
        except Exception as e:
            logger.error(f"Could not create SOPs directory '{sops_dir}': {e}", exc_info=True)
            return jsonify({"success": False, "message": f"Could not create SOPs directory: {str(e)}"}), 500

    if 'file' not in request.files:
        logger.warning("No file part in upload_sop request.")
        return jsonify({"success": False, "message": "No file part in the request."}), 400
    
    file = request.files['file']
    if file.filename == '':
        logger.warning("No file selected for upload_sop request.")
        return jsonify({"success": False, "message": "No file selected."}), 400

    if file:
        try:
            filename = secure_filename(file.filename)
            file_path = os.path.join(sops_dir, filename)
            file.save(file_path)
            logger.info(f"File '{filename}' uploaded successfully to '{sops_dir}'.")
            # After uploading, it's a good idea to mark SOPs as not processed
            # so the user is prompted to re-process them.
            app_state["sops_processed"] = False
            app_state["qa_chain"] = None # Clear the chain as well
            logger.info("Marked SOPs as not processed and cleared QA chain due to new file upload.")
            return jsonify({"success": True, "message": f"File '{filename}' uploaded successfully. Please re-process SOPs."}), 200
        except Exception as e:
            logger.error(f"Error saving uploaded file '{file.filename}': {e}", exc_info=True)
            return jsonify({"success": False, "message": f"Error saving file: {str(e)}"}), 500
    
    return jsonify({"success": False, "message": "File upload failed for an unknown reason."}), 500

if __name__ == '__main__':
    # initialize_app() handles API key loading and LLM setup.
    if not initialize_app():
        logger.warning("Application initialization failed in __main__. Check logs for details. App will still run but may not be fully functional.")

    logger.info("Starting Flask app on host 0.0.0.0, port 5001")
    app.run(host='0.0.0.0', port=5001, debug=True, reloader_type="stat")
