# Project GRAIL Chatbot - Change Log

All notable changes to this project will be documented in this file.

---

## [Unreleased] - 2025-06-03

### Changed
- **Migrated to GenAI API**: Switched from direct Google Generative AI SDK to the new GenAI API service.
  - The application now uses the `gemini-2.0-flash` model via the GenAI API.
  - Authentication is handled using a service account JSON file and ID tokens.
  - `gemini_handler.py` was significantly refactored:
    - Introduced `CustomGenAILLM`, a custom Langchain LLM class, to interface with the GenAI API.
    - Updated configuration loading to use new environment variables for GenAI API key (`GenAI_API_KEY`), ADID (`MY_P_NO`), and service account file path (`SERVICE_ACCOUNT_FILE_PATH`).
  - `config.py` was updated with new settings for the GenAI API (URL, deployment name, max tokens, and environment variable names).
  - Added `google-auth` and `google-auth-oauthlib` to `requirements.txt` for the new authentication mechanism.
- **Switched to Local Embeddings**: Replaced `GoogleGenerativeAIEmbeddings` with `HuggingFaceEmbeddings` (using the `all-MiniLM-L6-v2` model) for document embeddings. This removes the dependency on the Google API key for the embedding generation process and allows for offline/free embedding capabilities.
  - Modified `vector_store_manager.py` to initialize and use `HuggingFaceEmbeddings`.
  - Removed the `get_gemini_api_key_for_embeddings` function from `gemini_handler.py` as it is no longer required.
  - Added `sentence-transformers` to `requirements.txt` as a new dependency.
  - Commented out the `EMBEDDING_MODEL_NAME` configuration in `config.py` as the model name is now hardcoded in `vector_store_manager.py`.

### Added
- **Markdown Rendering for Chat Responses**: Enhanced the chatbot to support Markdown formatting in its responses.
  - Updated the system prompt in `gemini_handler.py` to instruct the LLM to generate Markdown-formatted answers.
  - Added `react-markdown` to the frontend dependencies.
  - Modified `frontend/src/App.js` to use `ReactMarkdown` for rendering bot messages, allowing for lists, bold/italic text, and other Markdown features to be displayed correctly.

---

## [Unreleased] - 2025-05-29

### Added
- Created this `CHANGELOG.md` file to track all changes.

### Changed
- Standardized text chunk handling to use Langchain `Document` objects instead of Python dictionaries. `utils.get_text_chunks` now returns a list of `Document` objects. `vector_store_manager.create_vector_store` was updated to use `FAISS.from_documents` and to pickle/unpickle lists of `Document` objects in `text_chunks.pkl`. This resolved a `TypeError` related to `Document` objects not being subscriptable.
- The chatbot interface now displays an initial welcome message: `Hello! How can I help you today?` This appears when the chat first loads and after the chat is cleared.
- The chatbot header displays `tata_steel_blue_svg.svg` (imported as `tataSteelBlueLogo`) on the left and `tata_svg.svg` (imported as `tataBlueLogo`) on the right. Both logos are in `frontend/src/logo/` and have a maxHeight of `35px`. The main application title `Project GRAIL Chatbot` is centered between them.
- The logo image files for the chatbot application (e.g., `tata_steel_blue.png`, `tata_blue.png`) are located in the `frontend/src/logo/` directory, not `frontend/src/assets/`.
- The custom MUI theme is generated from scratch in `frontend/src/index.js` using the `getDesignTokens` function. All required theme objects and properties (like `palette.common`, `palette.action`, `shadows`, `zIndex`, `spacing`, `breakpoints`, `transitions`, and `mixins`) are defined to avoid runtime errors.
- UI elements such as chatboxes, message bubbles, input fields, buttons, and admin panels now use a border-radius of 4px for a 'sharper' and 'less rounded' look (changed from 8px to 4px).

---

> For future changes, please add entries above this line with the date and a summary of the modifications.
