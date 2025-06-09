# CODEBASE_OVERVIEW

## Project Purpose
This codebase implements a production-grade Retrieval Augmented Generation (RAG) chatbot for Tata Steel. The chatbot answers user questions based on Standard Operating Procedures (SOPs) by combining semantic search (vector retrieval) and the Gemini 2.0 Flash Large Language Model (LLM) via the GenAI API. The system is designed for reliability, extensibility, and ease of use by both end-users and administrators.

---

## High-Level Architecture

- **Backend (Python):**
  - Flask REST API provides endpoints for chat, admin actions, SOP upload, and system status.
  - Uses LangChain for LLM orchestration and retrieval pipeline.
  - FAISS for fast vector search over SOP chunks.
  - HuggingFace Transformers for local, cost-free embeddings.
  - Handles authentication and secure API calls to Gemini GenAI API.
- **Frontend (React):**
  - Material UI-based chat and admin interface.
  - Allows users to chat with the bot and admins to process, upload, and view SOP files.
  - Communicates with backend via REST API.

---

## File-by-File Breakdown & Connections

### Backend (Python)

- **app.py**
  - Entry point for the backend (Flask app).
  - Defines all REST API endpoints:
    - `/api/status`: System health and config status.
    - `/api/process_sops`: Loads, chunks, and indexes SOPs (triggers embedding and FAISS index creation).
    - `/api/ask`: Accepts user questions, retrieves relevant SOP chunks, and gets answers from the LLM.
    - `/api/list_sops`: Lists all SOP files available in the SOP directory.
    - `/api/upload_sop`: Allows admin to upload new SOP files securely.
  - Manages application state (e.g., whether SOPs are processed, QA chain cache).
  - Delegates document loading/chunking to `utils.py`, vector store management to `vector_store_manager.py`, and LLM calls to `gemini_handler.py`.
  - Loads configuration from `config.py` and environment variables.

- **config.py**
  - Centralizes all configuration:
    - SOP directory path (`SOP_DIR_PATH`)
    - Model/deployment names
    - API URLs and keys
    - Text chunking parameters
    - Logging and environment variable names
  - Makes it easy to adapt the app to new environments or requirements.

- **utils.py**
  - Handles SOP file loading and preprocessing:
    - PDF parsing via `PyMuPDF (fitz)`
    - DOCX parsing via `python-docx`
    - TXT file reading
    - Smart chunking of text for retrieval (using configurable chunk size/overlap)
    - Returns LangChain `Document` objects for downstream use
  - Ensures all document types are normalized for embedding and retrieval.

- **vector_store_manager.py**
  - Manages creation, persistence, and querying of the FAISS vector store:
    - Uses `HuggingFaceEmbeddings` (MiniLM model) for local, free, high-quality embeddings
    - Serializes and deserializes the vector store and text chunks using `pickle`
    - Exposes retriever interface for use by the QA chain in `app.py`

- **gemini_handler.py**
  - Implements a custom LangChain LLM class to wrap the Gemini GenAI API.
  - Handles:
    - Prompt formatting
    - Secure authentication (using `google-auth` and service account JSON)
    - Token management
    - Streaming and synchronous API calls
  - Exposes a standard LangChain LLM interface for use in the QA chain.

- **faiss_index/**
  - Directory for persistent vector store files:
    - `sop_index.faiss`: FAISS index data
    - `sop_index.pkl`: Pickled metadata
    - `text_chunks.pkl`: Pickled LangChain Document chunks
  - Allows for fast reload and avoids reprocessing on every startup.

- **sops/**
  - Directory for all SOP files to be ingested and queried.
  - Can be managed via admin UI (upload/delete) or by placing files manually.

- **requirements.txt**
  - Lists all backend dependencies (see below for rationale).

- **gemini_api_key.env**
  - Stores sensitive credentials (service account JSON path, GenAI API key, ADID).
  - Must NOT be committed to version control.

- **app.log**
  - Log file for backend operations and errors.

---

### Frontend (React)

- **frontend/src/App.js**
  - Main chat interface for users.
  - Handles user input, displays bot and user messages, and renders Markdown answers.
  - Communicates with backend via `/api/ask` and status endpoints.
  - Integrates Tata Steel branding and custom theming.

- **frontend/src/AdminPage.js**
  - Admin interface for system status, SOP processing, file upload, and SOP file listing.
  - Calls `/api/process_sops`, `/api/list_sops`, `/api/upload_sop`, and `/api/status` endpoints.
  - Provides upload controls, file list, and process/refresh actions.
  - Handles UI feedback, error handling, and loading states.

- **frontend/src/logo/**
  - Contains all logo and branding assets (PNG, SVG) for Tata Steel and Tata.

- **frontend/src/index.js**
  - Entry point for the React app.
  - Sets up theme (Material UI), global styles, and renders the app.

- **frontend/src/components/**
  - (If present) Shared React components for UI modularity.

---

## Backend/Frontend Flow

1. **Admin uploads SOPs** (via AdminPage UI or direct file placement in `sops/`).
2. **Admin triggers SOP processing** (`/api/process_sops`):
   - Backend loads all SOPs, chunks them, generates embeddings, and builds FAISS index.
   - Metadata and vector store are persisted for fast reload.
3. **User asks a question** (via chat UI):
   - Frontend sends question to `/api/ask`.
   - Backend retrieves top-N relevant SOP chunks using FAISS.
   - Backend sends context and question to Gemini LLM via GenAI API.
   - LLM response is returned to frontend and rendered (Markdown supported).
4. **Admin can view SOP files, upload new ones, or reprocess as needed.**

---

## Library Choices & Rationale

- **Flask:** Lightweight, easy to use, widely supported for REST APIs.
- **LangChain:** Provides a modular way to build LLM pipelines, supports custom LLMs and retrievers.
- **FAISS:** Industry-standard for fast, scalable vector search, crucial for efficient RAG.
- **HuggingFace Transformers & sentence-transformers:** Free, high-quality local embeddings (MiniLM), avoids API costs and latency.
- **PyMuPDF (fitz):** Robust PDF parsing, better than PyPDF2 for complex documents.
- **python-docx:** Reliable DOCX parsing.
- **google-auth, google-auth-oauthlib:** Secure, standards-based authentication for GenAI API.
- **pickle:** Fast, simple serialization of Python objects (vector store, chunks).
- **Material UI (frontend):** Modern, accessible, and themeable React UI library.

---

## Deployment Steps & Precautions

### Steps
1. **Backend:**
   - Set up Python virtual environment and install dependencies.
   - Place service account JSON and API key in `gemini_api_key.env` (never commit this file).
   - Ensure `config.py` paths (especially `SOP_DIR_PATH`) are correct for your deployment environment.
   - Use a production WSGI server (e.g., Gunicorn) and reverse proxy (e.g., Nginx) for serving Flask in production.
   - Monitor and rotate `app.log` to avoid disk bloat.
2. **Frontend:**
   - Install dependencies and build with `npm run build`.
   - Serve static files using a production server (Nginx, serve, or Flask static route).
   - Restrict CORS in `app.py` to only allow your frontend domain.

### Precautions
- **Security:** Never commit `gemini_api_key.env` or service account files to version control. Use environment variables or vaults for secrets in production.
- **API Keys:** Protect all credentials and rotate regularly.
- **Scaling:** For high load, run multiple backend instances and use a load balancer.
- **Static Files:** Serve frontend build from a secure, fast static server.
- **Dependencies:** Pin all dependency versions for reproducibility.
- **SOP Directory:** Ensure `SOP_DIR_PATH` is writable and backed up if needed.
- **User Data:** No user data is persisted except logs and uploaded SOPs; ensure compliance with internal policies.

---

## Summary Table: File Purpose & Connections

| File/Dir                     | Purpose / Connection                                                        |
|-----------------------------|-----------------------------------------------------------------------------|
| app.py                      | Flask REST API, routes, state, delegates to utils/vector_store_manager/LLM   |
| config.py                   | All configuration (paths, chunk size, env vars, model names, etc.)           |
| utils.py                    | SOP loading/chunking, returns LangChain Documents                            |
| vector_store_manager.py     | FAISS vector store creation/query, embedding management                      |
| gemini_handler.py           | Custom LangChain LLM for GenAI API, handles auth and prompt                  |
| faiss_index/                | Persistent FAISS index and chunk cache                                       |
| sops/                       | Directory for all SOP files (uploaded or manual)                             |
| requirements.txt            | Backend dependencies                                                         |
| gemini_api_key.env          | API/service account secrets (never commit)                                   |
| app.log                     | Backend logs                                                                 |
| frontend/src/App.js         | Main chat UI, communicates with backend                                      |
| frontend/src/AdminPage.js   | Admin UI: status, SOP upload/list/process                                    |
| frontend/src/logo/          | Tata Steel branding assets                                                   |
| frontend/src/index.js       | React entry point, theme, global styles                                      |
| frontend/src/components/    | (If present) Shared React UI components                                      |

---

## For Further Development
- Add user authentication for chat/admin separation if needed.
- Consider adding SOP file deletion and versioning.
- Monitor and optimize embedding and LLM performance for large SOP sets.
- Extend admin UI for more granular system controls.

---

*This document is intended for developers, admins, and maintainers of the Project GRAIL Chatbot.*


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
    - Embeds text chunks using the `all-MiniLM-L6-v2` model from the `sentence-transformers` library. This is accessed via the `HuggingFaceEmbeddings` wrapper from `langchain-community`, and removes the previous dependency on Google's online embedding services and associated API keys for this part of the process. The embeddings are stored in a FAISS vector store for fast retrieval.
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
