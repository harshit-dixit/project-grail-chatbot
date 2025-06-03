# Project GRAIL Chatbot

A modern, production-grade chatbot that answers questions based on Standard Operating Procedures (SOPs) using Retrieval Augmented Generation (RAG) and the GenAI API (Gemini 2.0 Flash model). Built for Tata Steel, it features a robust Python backend and a user-friendly React frontend.

---

## Features

- **Document Ingestion**: Supports `.txt`, `.pdf`, `.docx` SOPs
- **Smart Chunking**: Efficiently splits documents for retrieval
- **Semantic Search**: Uses FAISS and HuggingFace embeddings for fast, accurate retrieval
- **GenAI Integration**: Answers are generated using the Gemini 2.0 Flash model via a secure API
- **Modern Frontend**: Responsive React app with Tata branding and Material UI
- **Admin Panel**: Manage SOP processing and system status
- **Secure Auth**: Service account and API key based authentication

---

## Architecture Overview

- **Backend**: Python (Flask), LangChain, FAISS, HuggingFace, Google Auth
- **Frontend**: React (MUI), communicates with Flask backend
- **AI Model**: GenAI API (Gemini 2.0 Flash) via custom LangChain LLM
- **Document Store**: FAISS index with chunked SOPs (vector_store_manager.py)

---

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

## Usage

3. Set up the Backend (Python/Flask):

Open a terminal or command prompt on your work laptop.
Navigate into the cloned project directory (e.g., cd path/to/project-grail-chatbot).

Create and activate a Python virtual environment (highly recommended):
python -m venv venv (This creates a venv folder)
On Windows: venv\Scripts\activate
On macOS/Linux: source venv/bin/activate

Install Python dependencies:
With your virtual environment active, run: pip install -r requirements.txt
Create the API Key File:
In the project's root directory on your work laptop, manually create the gemini_api_key.env file (this file was ignored by Git and thus not cloned).
Add your Google API key to it:
CopyInsert
GOOGLE_API_KEY='YOUR_ACTUAL_GOOGLE_API_KEY'
SOPs/Data Directory:
Your config.py specifies SOP_DIR_NAME = "sops". Create this sops directory in the project root on your work laptop if it doesn't exist.
Copy your SOP documents (PDFs, DOCX, TXT files) into this sops directory. (These were likely not uploaded to GitHub if they are large or numerous).
4. Set up the Frontend (React):

In your terminal, navigate to the frontend directory within your project: cd frontend
Install Node.js dependencies:
Run: ```bash npm install ```
5. Run the Application:

You'll need two terminals open.
Terminal 1: Start the Backend (Flask):
Make sure you are in the project's root directory (path/to/project-grail-chatbot).
Ensure your Python virtual environment (venv) is activated.
Run: ```bash python app.py ```
You should see output indicating the Flask server is running (usually on http://127.0.0.1:5000/).
Terminal 2: Start the Frontend (React):
Navigate to the frontend directory (path/to/project-grail-chatbot/frontend).
Run: ```bash npm start ```
This will usually open the application automatically in your web browser at http://localhost:3000. If not, open it manually.




Method 2: Manual Copy (If not using Git or no remote repository)

On your current laptop:
Locate your main project directory: C:\Users\seema\Desktop\AI\windsurf\chatbot
Copy this entire chatbot folder to a USB drive, network share, or use a cloud storage service (like OneDrive, Google Drive, Dropbox) to transfer it.
Important: When copying, you can usually exclude the frontend/node_modules folder and the Python virtual environment folder (e.g., venv, .venv) if you have one in the backend. These can be very large and are easily recreated.
On your work laptop:
Copy the chatbot folder from your transfer medium to your desired location.
Regardless of the transfer method, you'll need to set up the environment on your work laptop:

Install Prerequisites:
Python: Ensure Python is installed (preferably the same version you used, or a compatible one).
Node.js and npm: Ensure Node.js (which includes npm) is installed for the frontend.
Set up Backend (Python):
Navigate to your backend directory (e.g., C:\path\to\chatbot\).
It's highly recommended to use a virtual environment:
bash
CopyInsert
```bash python -m venv venv ```
.\venv\Scripts\activate  # On Windows
# source venv/bin/activate # On macOS/Linux

Install Python dependencies:
bash
CopyInsert in Terminal
pip install -r requirements.txt
Set up Frontend (React):
Navigate to your frontend directory (e.g., C:\path\to\chatbot\frontend\).
Install Node.js dependencies:
bash
CopyInsert in Terminal
npm install

API Key:
Crucially, you will need to recreate your gemini_api_key.env file in the root of the chatbot directory on your work laptop. Add your GOOGLE_API_KEY=YOUR_ACTUAL_KEY to this file. Do not commit this file to public Git repositories. If you are using Git, ensure .env or *.env is listed in your .gitignore file.

Verify Logo Paths (if manual copy):
If you manually copied and had any issues with logo paths recently, just double-check they are correct relative to App.js (frontend/src/logo/ was the last setup).
Running the Application on your Work Laptop:

Once everything is set up:

Start the Backend (Flask):
Open a terminal in the chatbot directory (with your Python virtual environment activated).
Run: python app.py
Start the Frontend (React Dev Server):
Open another terminal in the chatbot/frontend directory.
Run: npm start
This should get Project GRAIL up and running on your work machine. The key is to replicate the file structure and reinstall all dependencies.



This will open the chatbot interface in your web browser.
