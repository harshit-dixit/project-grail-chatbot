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


# --- GenAI API Client --- 
class CustomGenAILLM(LLM):
    """Custom Langchain LLM to interact with the GenAI API."""
    api_url: str = config.GENAI_API_URL
    deployment_name: str = config.GENAI_DEPLOYMENT_NAME
    temperature: float = 0.7  # Default temperature as a class attribute
    max_tokens: str = config.GENAI_MAX_TOKENS
    
    # Credentials from environment
    service_account_file: Optional[str] = None
    api_key: Optional[str] = None
    adid: Optional[str] = None
    authed_session: Optional[AuthorizedSession] = None

    def __init__(self, **kwargs: Any): # temperature will be handled by Pydantic via class attribute or kwargs
        super().__init__(**kwargs)
        # self.temperature is now set by Pydantic from class default or kwargs
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
            {"role": "system", "content": "You are a humble AI assistant that helps people find information. Please format your responses using Markdown. For example, use bullet points for lists (e.g., * item), and use asterisks or underscores for bold (e.g., **bold text**) or italic text (e.g., *italic text*). If you need to present tabular data, use Markdown table syntax."},
            {"role": "user", "content": prompt}
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

def get_llm(): # Removed model_name and temperature parameters
    """Initializes and returns the Custom GenAI LLM."""
    logger.info(f"Initializing LLM via CustomGenAILLM.")
    # CustomGenAILLM now uses its own default temperature or one passed to its constructor if needed.
    # It reads deployment_name directly from config.
    try:
        # Pass the default temperature or allow it to be configured if necessary
        llm = CustomGenAILLM() # Uses default temperature 0.7
        logger.info("CustomGenAILLM initialized successfully.")
        return llm
    except Exception as e:
        logger.error(f"Error initializing CustomGenAILLM: {e}")
        raise RuntimeError(f"Failed to initialize LLM: {e}")

def get_conversational_chain(llm, retriever):
    """Creates and returns a conversational QA chain using the provided LLM and retriever."""
    if not llm or not retriever:
        logger.error("LLM or retriever not provided to get_conversational_chain.")
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
