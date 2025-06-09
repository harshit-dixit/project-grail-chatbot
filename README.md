# Project GRAIL Chatbot

A modern, production-grade chatbot that answers questions based on Standard Operating Procedures (SOPs) using Retrieval Augmented Generation (RAG) and the GenAI API (Gemini 2.0 Flash model). Built for Tata Steel, it features a robust Python backend and a user-friendly React frontend.

---

## Features

- **Document Ingestion**: Upload and process `.txt`, `.pdf`, `.docx` SOPs
- **Smart Chunking**: Efficiently splits documents for retrieval
- **Semantic Search**: Uses FAISS and HuggingFace embeddings for fast, accurate retrieval
- **GenAI Integration**: Answers are generated using the Gemini 2.0 Flash model via a secure API
- **Modern Frontend**: Responsive React app with Tata branding and Material UI
- **Admin Panel**: Manage SOP processing, upload/view SOP files, and check system status
- **Secure Auth**: Service account and API key based authentication

---

## CODEBASE_OVERVIEW

### Purpose
This codebase implements a RAG-based chatbot for Tata Steel, answering questions from SOP documents using a combination of semantic retrieval (FAISS, HuggingFace) and the Gemini 2.0 Flash LLM via a secure GenAI API.

### Main Components & File Interconnections

#### Backend (Python)
- **app.py**: Main Flask app. Orchestrates API endpoints (`/api/status`, `/api/process_sops`, `/api/ask`, `/api/list_sops`, `/api/upload_sop`), loads config, manages app state, and delegates to utility modules.
- **config.py**: Centralizes all configuration (paths, model names, API URLs, env vars, chunk sizes).
- **utils.py**: Loads and chunks SOPs (PDF, TXT, DOCX), returns LangChain Document objects. Uses `PyMuPDF` for PDF, `python-docx` for DOCX.
- **vector_store_manager.py**: Builds FAISS index from documents, manages retriever creation and persistence. Uses `HuggingFaceEmbeddings` for local, free embeddings.
- **gemini_handler.py**: Wraps GenAI API as a custom LangChain LLM, handles authentication (`google-auth`, `google-auth-oauthlib`) and prompt formatting.
- **faiss_index/**: Stores FAISS index and chunk cache (pickled with Python's `pickle`).
- **sops/**: Directory for user-uploaded SOPs (managed via admin UI and backend endpoints).
- **requirements.txt**: Python dependencies (see below for library rationale).

#### Frontend (React)
- **frontend/src/App.js**: Main chat interface. Handles user input, displays chat, and communicates with Flask backend.
- **frontend/src/AdminPage.js**: Admin UI for status, SOP processing, file upload, and file list. Uses Material UI and custom icons.
- **frontend/src/logo/**: Tata Steel and Tata branding assets.
- **frontend/src/index.js**: Entry point, theme, and global styles.

#### File & Module Connections
- Frontend calls Flask API endpoints for:
  - `/api/status`: System health
  - `/api/process_sops`: Triggers SOP loading, chunking, and vector store creation
  - `/api/ask`: Chatbot Q&A
  - `/api/list_sops`: Lists SOP files in backend
  - `/api/upload_sop`: Uploads new SOP files
- Backend processes requests, manages vector store, and invokes GenAI API for answers.
- All configuration is managed in `config.py` and `.env` files.

### Key Python Libraries & Why Used
- **Flask**: REST API backend, easy integration with React frontend.
- **LangChain**: Standardizes LLM and retrieval pipeline, custom LLM for GenAI API.
- **FAISS**: Fast, scalable vector search for document retrieval.
- **HuggingFace Transformers**: Local, free document embeddings (no API cost).
- **PyMuPDF (fitz)**: Robust PDF parsing.
- **python-docx**: DOCX file parsing.
- **google-auth, google-auth-oauthlib**: Secure service account authentication for GenAI API.
- **pickle**: Efficient serialization of vector stores and document chunks.
- **sentence-transformers**: Used for HuggingFace embedding models.

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd chatbot
```

### 2. Backend Setup (Python/Flask)

**a. Create and activate a virtual environment:**
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On macOS/Linux
```

**b. Install Python dependencies:**
```bash
pip install -r requirements.txt
```

**c. Configure API Keys and Service Account:**
- Copy your Google Cloud service account JSON to the project root.
- Create `gemini_api_key.env` in the root with:
  ```
  SERVICE_ACCOUNT_FILE_PATH=svc-genai-api-dev-oneit.json
  GenAI_API_KEY=your_genai_api_key
  MY_P_NO=your_adid
  ```
- Edit `config.py` if you need to change API URLs, model, or SOP directory.

**d. Add SOP documents:**
- Place your `.pdf`, `.docx`, or `.txt` files in the `sops/` directory (or upload via the admin UI).

**e. Run the backend:**
```bash
python app.py
```
The backend will be available at `http://127.0.0.1:5001/`

### 3. Frontend Setup (React)
```bash
cd frontend
npm install
npm start
```
The frontend will run on `http://localhost:3000/` and proxy API calls to the Flask backend.

---

## Usage

1. **Open the frontend** at [http://localhost:3000/](http://localhost:3000/)
2. **Admin Panel**: Click the settings icon to access the Admin page. Here you can process SOPs, upload/view files, and check backend/API status.
3. **Chat**: Ask questions. The chatbot will retrieve relevant SOP chunks and generate answers using the Gemini model.
4. **Clear Chat**: Use the clear icon to reset the conversation.

---

## Environment Variables
- `SERVICE_ACCOUNT_FILE_PATH`: Path to your Google Cloud service account JSON
- `GenAI_API_KEY`: API key for GenAI API
- `MY_P_NO`: Your ADID (for authentication)

---

## Customization & Advanced
- **SOP Chunking**: Tune `TEXT_CHUNK_SIZE` and `TEXT_CHUNK_OVERLAP` in `config.py`
- **Model/Deployment**: Change `GENAI_DEPLOYMENT_NAME` or API URL in `config.py`
- **UI**: Update logos in `frontend/src/logo/` and tweak theme in `frontend/src/index.js`

---

## Troubleshooting
- **API Key/Service Account errors**: Check `gemini_api_key.env` and logs in `app.log`
- **No answers**: Ensure SOPs are processed (see Admin Panel)
- **Vector store issues**: Delete `faiss_index/` to force a rebuild

---

## Deployment Guide & Precautions

### Steps
1. **Backend:**
   - Set up a Python virtual environment.
   - Install dependencies with `pip install -r requirements.txt`.
   - Place your service account JSON and API key in `gemini_api_key.env`.
   - Ensure `config.py` paths (especially `SOP_DIR_PATH`) are correct for the deployment environment.
   - Place SOP files in the `sops/` directory (or upload via admin UI).
   - Run `python app.py` (for production, use Gunicorn or another WSGI server).
2. **Frontend:**
   - In `frontend/`, run `npm install`.
   - Build the frontend with `npm run build` for production.
   - Serve static files with a production server (e.g., Nginx, serve, or Flask static route).

### Precautions
- **Security:** Never commit `gemini_api_key.env` or service account files to version control.
- **CORS:** For production, restrict CORS in `app.py` to only allow your frontend domain.
- **API Keys:** Always use environment variables or secure vaults for keys in production.
- **Static Files:** Ensure the frontend build is served from a secure, fast static server.
- **Logging:** Monitor and rotate logs (`app.log`) to avoid disk bloat.
- **Dependencies:** Pin dependency versions for reproducibility.
- **Scaling:** For high load, use a production WSGI server (e.g., Gunicorn) and a reverse proxy (e.g., Nginx).

---

## License

Proprietary. For Tata Steel internal use only.

## Project Structure

```
chatbot/
├── app.py                  # Flask REST API backend
├── config.py               # All backend configuration
├── utils.py                # SOP loading & chunking
├── vector_store_manager.py # FAISS index management
├── gemini_handler.py       # GenAI API integration (LangChain LLM)
├── requirements.txt        # Python dependencies
├── gemini_api_key.env      # API/service account secrets (not committed)
├── sops/                   # Place your SOP documents here
├── faiss_index/            # Vector DB and chunk cache
├── frontend/
│   ├── src/
│   │   ├── App.js          # Main React app
│   │   ├── AdminPage.js    # Admin interface
│   │   ├── logo/           # Tata Steel logos
│   │   └── ...
│   └── ...
└── README.md
```

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd chatbot
```

### 2. Backend Setup (Python/Flask)

**a. Create and activate a virtual environment:**

```bash
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On macOS/Linux
```

**b. Install Python dependencies:**

```bash
pip install -r requirements.txt
```

**c. Configure API Keys and Service Account:**

- Copy your Google Cloud service account JSON to the project root.
- Create `gemini_api_key.env` in the root with:

```
SERVICE_ACCOUNT_FILE_PATH=svc-genai-api-dev-oneit.json
GenAI_API_KEY=your_genai_api_key
MY_P_NO=your_adid
```

- Edit `config.py` if you need to change API URLs, model, or SOP directory.

**d. Add SOP documents:**

- Place your `.pdf`, `.docx`, or `.txt` files in the `sops/` directory.

**e. Run the backend:**

```bash
python app.py
```

The backend will be available at `http://127.0.0.1:5001/`

### 3. Frontend Setup (React)

```bash
cd frontend
npm install
npm start
```

The frontend will run on `http://localhost:3000/` and proxy API calls to the Flask backend.

---

## Usage

1. **Open the frontend** at [http://localhost:3000/](http://localhost:3000/)
2. **Admin Panel**: Click the settings icon to access the Admin page. Here you can process SOPs and check backend/API status.
3. **Chat**: Ask questions. The chatbot will retrieve relevant SOP chunks and generate answers using the Gemini model.
4. **Clear Chat**: Use the clear icon to reset the conversation.

---

## Environment Variables

- `SERVICE_ACCOUNT_FILE_PATH`: Path to your Google Cloud service account JSON
- `GenAI_API_KEY`: API key for GenAI API
- `MY_P_NO`: Your ADID (for authentication)

---

## Tech Stack

- **Backend**: Python, Flask, LangChain, FAISS, HuggingFace, Google Auth
- **Frontend**: React, Material UI
- **AI**: GenAI API (Gemini 2.0 Flash)

---

## Customization & Advanced

- **SOP Chunking**: Tune `TEXT_CHUNK_SIZE` and `TEXT_CHUNK_OVERLAP` in `config.py`
- **Model/Deployment**: Change `GENAI_DEPLOYMENT_NAME` or API URL in `config.py`
- **UI**: Update logos in `frontend/src/logo/` and tweak theme in `frontend/src/index.js`

---

## Troubleshooting

- **API Key/Service Account errors**: Check `gemini_api_key.env` and logs in `app.log`
- **No answers**: Ensure SOPs are processed (see Admin Panel)
- **Vector store issues**: Delete `faiss_index/` to force a rebuild

---

## License

Proprietary. For Tata Steel internal use only.


**b. Install dependencies:**
```bash
pip install -r requirements.txt
```

**c. Set up your Gemini API Key:**
- Obtain an API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
- Create a `.env` file in the root directory:
  ```
  GOOGLE_API_KEY="YOUR_GEMINI_API_KEY"
  ```

**d. Add SOP Documents:**
- Place your `.txt`, `.pdf`, or `.docx` files in the `sops/` directory.

---

### 3. Frontend Setup (React)

```bash
cd frontend
npm install
```

---

### 4. Running the Application

**Open two terminals:**

**Terminal 1: Start Backend**
```bash
cd chatbot
venv\Scripts\activate  # (if not already activated)
python app.py
```

**Terminal 2: Start Frontend**
```bash
cd chatbot/frontend
npm start
```

- The backend runs on [http://localhost:5001](http://localhost:5001)
- The frontend runs on [http://localhost:3000](http://localhost:3000)

---

## Deployment/Transfer to Another Machine

1. Copy the `chatbot` folder (excluding `venv` and `frontend/node_modules`) to your new machine.
2. Repeat the setup steps above.
3. Recreate `.env` with your API key on the new machine.

---

## Troubleshooting

- **API Key Errors:** Ensure your `.env` file exists and contains a valid `GOOGLE_API_KEY`.
- **Document Loading:** Confirm your SOP files are in the `sops/` directory.
- **Dependency Issues:** Reinstall dependencies (`pip install -r requirements.txt`, `npm install`).

---

## Contributing

Pull requests and suggestions are welcome! Please open an issue first to discuss changes.

---

## License

[MIT License](LICENSE) (if applicable)

---


This project implements a chatbot that answers questions based on a provided set of Standard Operating Procedures (SOPs). It uses Retrieval Augmented Generation (RAG) with the Google Gemini API.

## Features

-   Load SOP documents (e.g., .txt, .pdf, .docx).
-   Process and chunk documents for efficient retrieval.
-   Generate embeddings and store them in a vector database (FAISS).
-   Retrieve relevant document chunks based on user queries.
-   Use Google Gemini API to generate answers based on retrieved context.
-   Simple Streamlit interface for interaction.

## Project Structure

```
chatbot/
├── sops/                  # Directory to store your SOP documents
├── main.py                # Main application script (Streamlit UI)
├── utils.py               # Utility functions for document loading and processing
├── vector_store_manager.py # Manages vector store creation and querying
├── gemini_handler.py      # Handles interaction with the Gemini API
├── requirements.txt       # Python dependencies
├── .env                   # To store API keys (create this file)
└── README.md              # This file
```

## Setup

1.  **Navigate to your project directory:**
    ```bash
    cd C:\Users\seema\Desktop\AI\windsurf\chatbot
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    venv\Scripts\activate  # On Windows
    # source venv/bin/activate  # On macOS/Linux
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Google Gemini API Key:**
    *   Obtain an API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
    *   Create a file named `.env` in the `chatbot` directory.
    *   Add your API key to the `.env` file:
        ```
        GOOGLE_API_KEY="YOUR_GEMINI_API_KEY"
        ```

5.  **Add SOP Documents:**
    *   Place your SOP documents (e.g., `.txt`, `.pdf`, `.docx` files) into the `sops/` directory.

