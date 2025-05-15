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

Run the Streamlit application from the `chatbot` directory:

```bash
streamlit run main.py
```

This will open the chatbot interface in your web browser.
