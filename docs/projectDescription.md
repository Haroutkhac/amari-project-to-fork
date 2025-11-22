# Project Description

In this project, you’ll develop a production‑ready application that processes shipment documents and extracts data for the user. You may use any AI tools (OpenAI, Claude, Gemini, Cursor, GitHub Copilot, etc.). No human assistance is allowed.

**Guidelines**
- Prioritize tasks wisely; you’ll need to commit all code within the 3‑hour timeframe.
- A starter codebase is attached at the end of this document.
- Evaluation criteria include completion, attention to detail, error handling, coding practices, and software robustness.
- Feel free to be creative and note any assumptions at the end.

## Project Components

### API
- Create an API that accepts a list of document files and extracts relevant data.
- Supports multiple documents (PDFs and/or XLSX) related to a single shipment.

### Documents
- For testing, two documents are provided:
  - A bill of lading (`.pdf`).
  - A commercial invoice and packing list (`.xlsx`).

### LLM
- You can use the open ai API key in the .env file OPENAI_API_KEY
### UI
- Build a platform (React or any framework of your choice) with the following functionalities:
  1. Upload the documents to extract data.
  2. Show an editable form with pre‑filled data (fields to be extracted: `@googleform.txt`).
  3. Option to view the documents on the side with the extracted data for easy audit.

### Bonus Work
#### Deployment
- Containerize the application with Docker, include all dependencies, and set up networking between containers.

#### Evaluation
- Create an evaluation script that calculates accuracy, precision, recall, and F1 for the given documents to assess robustness.

#### Testing
- Write unit tests for the functions using the `pytest` library.

