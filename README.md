# SOP Chatbot with Python, RAG, and Gemini API

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
Run: npm install
5. Run the Application:

You'll need two terminals open.
Terminal 1: Start the Backend (Flask):
Make sure you are in the project's root directory (path/to/project-grail-chatbot).
Ensure your Python virtual environment (venv) is activated.
Run: python app.py
You should see output indicating the Flask server is running (usually on http://127.0.0.1:5000/).
Terminal 2: Start the Frontend (React):
Navigate to the frontend directory (path/to/project-grail-chatbot/frontend).
Run: npm start
This will usually open the application automatically in your web browser at http://localhost:3000. If not, open it manually.

```bash
streamlit run main.py
```

This will open the chatbot interface in your web browser.
