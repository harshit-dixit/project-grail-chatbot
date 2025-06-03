import os
import json
import logging
from typing import Any, List, Mapping, Optional, Dict

from dotenv import load_dotenv
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession

from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_core.documents import Document
from langchain_core.language_models.llms import LLM

import config

logger = logging.getLogger(__name__)

# --- Environment Loading --- 
def load_env_vars():
    """Loads environment variables from the .env file specified in config."""
    env_file_name = config.ENV_FILE_NAME
    dotenv_full_path = os.path.join(config.PROJECT_ROOT, env_file_name)
    if not load_dotenv(dotenv_path=dotenv_full_path):
        logger.warning(f"Could not find or load '{dotenv_full_path}'. Ensure it exists.")
    else:
        logger.info(f"Successfully loaded environment variables from '{dotenv_full_path}'.")

load_env_vars() # Load environment variables when the module is imported

# --- Function to get original Gemini API Key (for Embeddings) --- 
def get_gemini_api_key_for_embeddings():
    """Loads and returns the original GEMINI_API_KEY from the .env file for embeddings."""
    api_key = os.getenv("GEMINI_API_KEY") # Assumes load_env_vars() has been called
    if not api_key:
        # This error indicates that GEMINI_API_KEY is missing, which is specifically needed for embeddings.
        logger.error(f"GEMINI_API_KEY not found in environment. This key is required for GoogleGenerativeAIEmbeddings.")
        raise ValueError(f"GEMINI_API_KEY not found. Please ensure it's set in '{config.ENV_FILE_NAME}' for embeddings.")
    logger.info("Successfully retrieved GEMINI_API_KEY for embeddings.")
    return api_key

# --- GenAI API Client --- 
class CustomGenAILLM(LLM):
    """Custom Langchain LLM to interact with the GenAI API."""
    api_url: str = config.GENAI_API_URL
    deployment_name: str = config.GENAI_DEPLOYMENT_NAME
    temperature: float = config.LLM_TEMPERATURE # Retain original temperature setting
    max_tokens: str = config.GENAI_MAX_TOKENS
    
    # Credentials from environment
    service_account_file: Optional[str] = None
    api_key: Optional[str] = None
    adid: Optional[str] = None
    authed_session: Optional[AuthorizedSession] = None

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self._load_credentials()
        self._initialize_session()

    def _load_credentials(self):
        """Loads credentials from environment variables."""
        self.service_account_file = os.getenv(config.SERVICE_ACCOUNT_FILE_ENV_VAR)
        self.api_key = os.getenv(config.GENAI_API_KEY_ENV_VAR)
        self.adid = os.getenv(config.ADID_ENV_VAR)

        if not self.service_account_file:
            raise ValueError(f"Service account file path not found. Set {config.SERVICE_ACCOUNT_FILE_ENV_VAR} in {config.ENV_FILE_NAME}")
        if not os.path.exists(self.service_account_file):
            raise FileNotFoundError(f"Service account file not found at path: {self.service_account_file}")
        if not self.api_key:
            raise ValueError(f"GenAI API key not found. Set {config.GENAI_API_KEY_ENV_VAR} in {config.ENV_FILE_NAME}")
        if not self.adid:
            raise ValueError(f"ADID not found. Set {config.ADID_ENV_VAR} in {config.ENV_FILE_NAME}")
        logger.info("GenAI credentials loaded successfully.")

    def _initialize_session(self):
        """Initializes the authenticated session for GenAI API calls."""
        try:
            creds = service_account.IDTokenCredentials.from_service_account_file(
                self.service_account_file,
                target_audience=self.api_url
            )
            self.authed_session = AuthorizedSession(creds)
            logger.info("GenAI authenticated session initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing GenAI authenticated session: {e}")
            raise ConnectionError(f"Failed to initialize GenAI authenticated session: {e}")

    @property
    def _llm_type(self) -> str:
        return "custom_genai_llm"

    def _call(
        self, 
        prompt: str, 
        stop: Optional[List[str]] = None, 
        run_manager: Optional[Any] = None, # CallbackManagerForLLMRun type hint if available
        **kwargs: Any
    ) -> str:
        """Makes a call to the GenAI API and returns the response."""
        if not self.authed_session:
            logger.error("Authenticated session is not available for GenAI API call.")
            raise ConnectionError("Authenticated session not initialized.")

        # The 'prompt' from RetrievalQA (using 'stuff' chain type) will contain
        # the system message, context, and question already formatted.
        # We need to structure this into the 'messages' array for GenAI.
        # Assuming the prompt is structured like:
        # "System message. Context: {context_str}. Question: {question_str}. Answer:"
        # We'll take the whole prompt as the user content for simplicity here.
        # A more robust solution might parse out system/user roles if needed.
        messages = [
            {"role": "system", "content": "You are an AI assistant that helps people find information."}, # Generic system prompt
            {"role": "user", "content": prompt} # The combined prompt from RetrievalQA
        ]

        payload = {
            'deployment_name': self.deployment_name,
            'temperature': str(self.temperature), # API expects string
            'adid': self.adid,
            'apikey': self.api_key,
            'messages': json.dumps(messages),
            'grounding': '1', # Enable Google Search for Gemini models
            'max_tokens': self.max_tokens
        }
        
        logger.debug(f"GenAI API Request Payload: {payload}")

        try:
            response = self.authed_session.post(self.api_url, data=payload, headers={})
            response.raise_for_status() # Raise an exception for HTTP errors
            response_json = response.json()
            logger.debug(f"GenAI API Response: {response_json}")

            # Extract the message content based on observed GenAI API response structure.
            # This might need adjustment if the actual response format differs.
            # Example: Gemini response might be in response_json['candidates'][0]['content']['parts'][0]['text']
            # Example: GPT-like response might be in response_json['choices'][0]['message']['content']
            
            # Let's try a common pattern for Gemini models first
            if 'candidates' in response_json and response_json['candidates']:
                content_parts = response_json['candidates'][0].get('content', {}).get('parts', [])
                if content_parts and 'text' in content_parts[0]:
                    return content_parts[0]['text']
            
            # Fallback for GPT-like or other structures
            if 'choices' in response_json and response_json['choices']:
                 message = response_json['choices'][0].get('message', {})
                 if 'content' in message:
                     return message['content']

            # If neither pattern matches, log and return a generic error or empty string
            logger.warning(f"Could not extract content from GenAI response. Full response: {response_json}")
            return "Error: Could not process response from AI service."
            
        except Exception as e:
            logger.error(f"Error during GenAI API call: {e}. Response: {response.text if 'response' in locals() else 'No response object'}")
            return f"Error communicating with AI service: {e}"

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {
            "api_url": self.api_url,
            "deployment_name": self.deployment_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

def get_llm(model_name=None, temperature=None):
    """Initializes and returns the Custom GenAI LLM."""
    # model_name and temperature from args are now for potential overrides if needed,
    # but CustomGenAILLM primarily uses config values.
    # For simplicity, we'll ignore them here and let CustomGenAILLM use its defaults from config.
    try:
        llm = CustomGenAILLM()
        logger.info("CustomGenAILLM initialized successfully.")
        return llm
    except Exception as e:
        logger.error(f"Error initializing CustomGenAILLM: {e}")
        # print(f"Error initializing LLM: {e}") # Keep print for direct script runs
        raise RuntimeError(f"Failed to initialize LLM: {e}")

def get_conversational_chain(llm, retriever):
    """Creates and returns a conversational QA chain using the provided LLM and retriever."""
    if not llm or not retriever:
        logger.error("LLM or retriever not provided to get_conversational_chain.")
        # print("Error: LLM or retriever not provided to get_conversational_chain.")
        return None

    # The prompt template here defines the structure that will be passed to CustomGenAILLM._call
    # The CustomGenAILLM._call method then wraps this into the 'messages' array for the GenAI API.
    prompt_template_str = """
    You are a friendly AI assistant. Answer the following question based *only* on the provided context.
    Be flexible and try to find relevant answer from documents and do not refer to the fact that you are answering based on the context.
    If the answer is not found in the context, say 'The answer is not available in the provided documents.'
    
    Context:\n{context}\n
    Question: {question}
    
    Answer:"""
    prompt = PromptTemplate(template=prompt_template_str, input_variables=["context", "question"])
    
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )
    logger.info("Conversational QA chain created successfully.")
    return chain

# Example usage (for testing purposes, can be removed or commented out later)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    logger.info("Starting gemini_handler.py example usage...")
    try:
        logger.info("Attempting to initialize LLM...")
        # Ensure your gemini_api_key.env file in the project root is configured with:
        # SERVICE_ACCOUNT_FILE_PATH='C:\path\to\your\svc-account.json'
        # GenAI_API_KEY='YOUR_GenAI_API_KEY'
        # MY_P_NO='YOUR_P_NO'
        
        llm = get_llm()
        if llm:
            logger.info("LLM Initialized successfully.")
            
            class DummyRetriever:
                def get_relevant_documents(self, query: str) -> List[Document]:
                    logger.debug(f"DummyRetriever: getting relevant documents for query: {query}")
                    return [Document(page_content="This is a dummy SOP about safety procedures.")]
                def invoke(self, query: str) -> List[Document]: # For Langchain 0.1.x compatibility if needed
                    logger.debug(f"DummyRetriever: invoking for query: {query}")
                    return self.get_relevant_documents(query)

            dummy_retriever = DummyRetriever()
            chain = get_conversational_chain(llm, dummy_retriever)
            
            if chain:
                logger.info("Conversational chain created successfully.")
                test_question = "What are the safety procedures?"
                logger.info(f"Sending test question to chain: {test_question}")
                response = chain.invoke({"query": test_question}) # Use invoke for newer Langchain
                logger.info(f"\nTest Question: {test_question}")
                logger.info(f"Test Answer: {response.get('result')}")
                logger.info(f"Source Documents: {response.get('source_documents')}")
            else:
                logger.error("Failed to create conversational chain.")
        else:
            logger.error("Failed to initialize LLM. Please check your environment variables and service account file.")

    except ValueError as ve:
        logger.error(f"Configuration Error: {ve}")
    except FileNotFoundError as fnfe:
        logger.error(f"File Not Found Error: {fnfe}")
    except ConnectionError as ce:
        logger.error(f"Connection Error: {ce}")
    except RuntimeError as rte:
        logger.error(f"Runtime Error: {rte}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
