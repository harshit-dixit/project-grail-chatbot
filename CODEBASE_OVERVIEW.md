# Chatbot Codebase Overview

Welcome! This guide will help you (especially if you’re a beginner) understand the structure, purpose, and workflow of the chatbot project. By the end, you’ll know how the system works, how to run it, and how to extend or debug it.

---

## 1. Project Purpose

This chatbot answers user questions based on a collection of SOP (Standard Operating Procedure) documents. It uses:
- **LangChain** for chaining LLMs and retrieval logic
- **FAISS** for vector search (finding relevant document chunks)
- **Google GenAI API** (via a custom LangChain LLM) for generating answers
- **Flask** for the backend API

---

## 2. High-Level Architecture

```
User (Frontend) → Flask API (app.py)
    → Loads/Chunks SOPs (utils.py)
    → Embeds/Indexes Chunks (vector_store_manager.py)
    → Retrieves Chunks (vector_store_manager.py)
    → Answers via LLM (gemini_handler.py → GenAI API)
```

---

## 3. Main Files & Their Roles

| File/Folders             | Purpose                                                                 |
|-------------------------|-------------------------------------------------------------------------|
| `app.py`                | Main Flask backend. Handles API endpoints, state, and workflow.         |
| `config.py`             | Central config (paths, API URLs, model names, etc).                     |
| `gemini_handler.py`     | Custom LLM client for GenAI API. Loads credentials, manages GenAI calls. |
| `vector_store_manager.py` | Handles embeddings, FAISS vector store creation/loading, retrieval.    |
| `utils.py`              | Loads and chunks SOP documents (PDF, DOCX, TXT).                        |
| `requirements.txt`      | Python dependencies.                                                     |
| `gemini_api_key.env`    | Environment variables (API keys, service account path, etc).            |
| `frontend/`             | (If present) Frontend code (React, etc).                                |
| `sops/`                 | Folder containing your SOP source documents.                            |

---

## 4. How the Chatbot Works (Workflow)

1. **Startup:**
    - `app.py` loads config and environment variables.
    - Initializes the LLM client (`CustomGenAILLM` via `gemini_handler.py`).
2. **Processing SOPs:**
    - Loads all documents from `sops/` (PDF, DOCX, TXT) using `utils.py`.
    - Splits each document into manageable text chunks with metadata.
    - Embeds chunks using Google’s embedding model (legacy Gemini API key).
    - Stores embeddings in a FAISS vector store for fast retrieval.
3. **Answering Questions:**
    - User sends a question to the Flask API (usually via a frontend).
    - The backend retrieves the most relevant document chunks using vector search.
    - The custom LLM (`CustomGenAILLM`) sends the user’s question and context to the GenAI API.
    - The API responds with an answer, which is returned to the user.

---

## 5. How to Run the Project (Setup)

1. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
2. **Prepare environment variables:**
   - Copy `gemini_api_key.env.example` to `gemini_api_key.env` (if example exists), or create it with:
     ```env
     GEMINI_API_KEY='...'           # For embeddings
     GenAI_API_KEY='...'            # For GenAI API
     MY_P_NO='...'                  # Your ADID
     SERVICE_ACCOUNT_FILE_PATH='...' # Path to your service account JSON
     ```
3. **Add your SOP documents** to the `sops/` folder (PDF, DOCX, or TXT).
4. **Run the backend:**
   ```sh
   python app.py
   ```
   - The Flask server will start (default: port 5001).
5. **(Optional) Run the frontend** if you have one (see `frontend/` for instructions).

---

## 6. How to Extend or Debug

- **Add More File Types:**
  - Edit `utils.py` to handle more document formats (e.g., markdown, HTML).
- **Change LLM or Embeddings:**
  - Update model names or API endpoints in `config.py`.
- **Switch Vector Database:**
  - For large-scale use, consider Pinecone, Weaviate, or another scalable vector DB.
- **Debugging:**
  - Check `app.log` for errors and info logs.
  - Use the logging output in the console for real-time feedback.
- **Testing:**
  - Move example/test code from each module into a `tests/` directory and use `pytest` for automated testing.

---

## 7. Common Pitfalls

- **Missing Environment Variables:**
  - Ensure all required variables are set in `gemini_api_key.env`.
- **Service Account Issues:**
  - The path must be correct and the file readable by Python.
- **API Key Issues:**
  - Both the legacy Gemini API key (for embeddings) and GenAI API key (for LLM) must be present.
- **SOP Directory Missing:**
  - Create the `sops/` folder and add your documents.

---

## 8. Where to Go Next

- Read the code for each module—start with `app.py` for the workflow, then `gemini_handler.py` for the LLM logic.
- Try adding a new SOP document and asking a question about it!
- Check the logs for detailed error messages if something doesn’t work.

---

Happy hacking! If you have questions, read the code comments or ask your team lead.
