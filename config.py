import os

# --- General Configuration ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# --- SOP Processing Configuration ---
# Default SOP directory is 'sops' inside the project root
SOP_DIR_NAME = "sops"
SOP_DIR_PATH = os.path.join(PROJECT_ROOT, SOP_DIR_NAME)
TEXT_CHUNK_SIZE = 1000
TEXT_CHUNK_OVERLAP = 200

# EMBEDDING_MODEL_NAME = "models/embedding-001"  # (deprecated, now using all-MiniLM-L6-v2 via HuggingFaceEmbeddings)

# --- API Key Configuration ---
# Name of the .env file containing API keys and service account path.
ENV_FILE_NAME = "gemini_api_key.env"

# --- GenAI API Configuration ---
GENAI_API_URL = "https://genai-api-development-one-it-423929642383.asia-south1.run.app"
GENAI_DEPLOYMENT_NAME = "gemini-2.0-flash" # Model to use via GenAI API
GENAI_MAX_TOKENS = "2048" # Max tokens for GenAI API (as string)
# Environment variable names for GenAI API credentials
SERVICE_ACCOUNT_FILE_ENV_VAR = "SERVICE_ACCOUNT_FILE_PATH"
GENAI_API_KEY_ENV_VAR = "GenAI_API_KEY"
ADID_ENV_VAR = "MY_P_NO"

# --- Logging Configuration ---
LOG_FILE_NAME = "app.log"
LOG_LEVEL = "INFO" # Can be DEBUG, INFO, WARNING, ERROR, CRITICAL

# Add any other global configurations here
# Example: MAX_DOCUMENT_SNIPPET_LENGTH = 250
