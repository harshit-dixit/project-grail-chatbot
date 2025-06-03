# Project GRAIL Chatbot - Change Log

All notable changes to this project will be documented in this file.

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
