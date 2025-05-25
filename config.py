import os

# --- General Configuration ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# --- SOP Processing Configuration ---
# Default SOP directory is 'sops' inside the project root
SOP_DIR_NAME = "sops"
SOP_DIR_PATH = os.path.join(PROJECT_ROOT, SOP_DIR_NAME)
TEXT_CHUNK_SIZE = 1000
TEXT_CHUNK_OVERLAP = 200

# --- Gemini LLM Configuration ---
# You can specify a different model if needed, e.g., "gemini-pro"
LLM_MODEL_NAME = "gemini-1.5-flash-latest"
# Temperature for the LLM (0.0 to 1.0). Lower values are more deterministic.
LLM_TEMPERATURE = 0.7 
EMBEDDING_MODEL_NAME = "models/embedding-001"

# --- API Key Configuration ---
# Name of the .env file containing the GOOGLE_API_KEY
ENV_FILE_NAME = "gemini_api_key.env"

# --- Logging Configuration ---
LOG_FILE_NAME = "app.log"
LOG_LEVEL = "INFO" # Can be DEBUG, INFO, WARNING, ERROR, CRITICAL

# Add any other global configurations here
# Example: MAX_DOCUMENT_SNIPPET_LENGTH = 250
