import os
import google.generativeai as genai
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_core.documents import Document
import config
import logging

logger = logging.getLogger(__name__)

def load_api_key():
    """Loads the Google API key from .env file."""
    env_file_name = config.ENV_FILE_NAME
    dotenv_full_path = os.path.join(config.PROJECT_ROOT, env_file_name)
    if not load_dotenv(dotenv_path=dotenv_full_path):
        logger.warning(f"Could not find or load '{dotenv_full_path}'. Ensure it exists.")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(f"GEMINI_API_KEY not found. Please ensure it's set in '{dotenv_full_path}' with: GEMINI_API_KEY='YOUR_KEY_HERE'")
    genai.configure(api_key=api_key)
    return api_key

def get_llm(model_name=None, temperature=None):
    """Initializes and returns the Gemini LLM."""
    resolved_model_name = model_name if model_name is not None else config.LLM_MODEL_NAME
    resolved_temperature = temperature if temperature is not None else config.LLM_TEMPERATURE
    try:
        api_key = load_api_key() # Ensures API key is configured
        llm = ChatGoogleGenerativeAI(model=resolved_model_name, 
                                   temperature=resolved_temperature,
                                   google_api_key=api_key, # Explicitly pass for clarity, though configure() also works
                                   convert_system_message_to_human=True) # Important for some RAG setups
        return llm
    except Exception as e:
        print(f"Error initializing LLM: {e}")
        return None


def get_conversational_chain(llm, retriever):
    """Creates and returns a conversational QA chain using the provided LLM and retriever."""
    if not llm or not retriever:
        print("Error: LLM or retriever not provided to get_conversational_chain.")
        return None

    prompt_template = """
    You are an friendly AI assistant. Answer the following question based *only* on the provided context.
    Be flexible and try to find relevant answer from documents and do not refer to the fact that you are answering based on the context.
    If the answer is not found in the context, say 'The answer is not available in the provided documents.'
    
    Context:\n{context}\n
    Question: {question}
    
    Answer:"""
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    
    # Using RetrievalQA chain as it's well-suited for this RAG task
    # It combines a retriever with a QA chain (like load_qa_chain)
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",  # 'stuff' puts all context into the prompt
        retriever=retriever,
        return_source_documents=True, # To see which documents were retrieved
        chain_type_kwargs={"prompt": prompt}
    )
    return chain

# Example usage (for testing purposes, can be removed or commented out later)
if __name__ == '__main__':
    try:
        print("Attempting to load API key and initialize LLM...")
        # Ensure you have your gemini_api_key.env file in the project root (C:\Users\seema\Desktop\AI\windsurf\chatbot)
        # with your actual Gemini API Key.
        # Example content for gemini_api_key.env:
        # GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
        
        llm = get_llm()
        if llm:
            print("LLM Initialized successfully.")
            
            # Dummy retriever for testing the chain structure
            # In a real scenario, this would come from vector_store_manager
            class DummyRetriever:
                def get_relevant_documents(self, query):
                    return [Document(page_content="This is a dummy SOP about safety procedures.")]
                def invoke(self, query):
                     return [Document(page_content="This is a dummy SOP about safety procedures. invoke method")]

            dummy_retriever = DummyRetriever()
            chain = get_conversational_chain(llm, dummy_retriever)
            
            if chain:
                print("Conversational chain created successfully.")
                # Test with a sample question
                test_question = "What are the safety procedures?"
                response = chain({"query": test_question}) # RetrievalQA expects 'query'
                print(f"\nTest Question: {test_question}")
                print(f"Test Answer: {response.get('result')}")
                print(f"Source Documents: {response.get('source_documents')}")
            else:
                print("Failed to create conversational chain.")
        else:
            print("Failed to initialize LLM. Please check your GEMINI_API_KEY in the gemini_api_key.env file.")
            print(f"Ensure the gemini_api_key.env file in the project root (C:\\Users\\seema\\Desktop\\AI\\windsurf\\chatbot) contains: GEMINI_API_KEY='YOUR_KEY'")

    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
