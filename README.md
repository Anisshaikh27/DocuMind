---
title: DocuMind
emoji: 🧠
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
short_description: AI-powered document Q&A — upload a PDF, ask questions.
---



DocuMind is a RAG-powered document Q&A system that lets users upload PDFs and ask grounded questions about their content.

## What it does

- Uploads a PDF and converts it into searchable document chunks.
- Retrieves the most relevant chunks for a user question.
- Generates an answer with source context from the uploaded document.

## Architecture

DocuMind follows a retrieval-augmented generation pipeline. A PDF is uploaded and parsed into raw text, then split into smaller chunks for easier semantic search. Each chunk is converted into an embedding and stored in a FAISS vector index. When a user asks a question, the system retrieves the most relevant chunks, sends them with the question to Claude, and returns a grounded answer with sources.

Pipeline:

```text
PDF -> chunks -> embeddings -> FAISS -> retrieval -> Claude -> answer
```

## Tech stack

| Area | Technology |
| --- | --- |
| Backend | FastAPI, Python |
| Frontend | React, Vite, Tailwind CSS |
| AI/LLM | Claude / OpenAI-compatible LLM API |
| Vector DB | FAISS |
| Evaluation | RAGAS |
| Deployment | Docker |

## Key concepts demonstrated

- Retrieval-Augmented Generation (RAG)
- Prompt engineering for grounded answers
- Hallucination guardrails for out-of-document questions
- RAGAS-based evaluation
- Docker deployment for a FastAPI backend

## Setup

### Backend

1. Create and activate a Python environment.

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

2. Install backend dependencies.

```bash
pip install -r backend/requirements.txt
```

3. Add your API key to `.env`.

```env
GROQ_API_KEY=your_api_key_here
```

4. Start the backend.

```bash
cd backend
uvicorn main:app --reload
```

### Frontend

1. Install frontend dependencies.

```bash
cd frontend/DocuMind
npm install
```

2. Start the frontend.

```bash
npm run dev
```

3. Open the app.

```text
http://127.0.0.1:5173
```

## API endpoints

| Method | Route | Description |
| --- | --- | --- |
| POST | `/upload` | Uploads a PDF, extracts text, creates chunks, generates embeddings, and stores them in FAISS. |
| POST | `/query` | Accepts a question and returns an answer with source chunks. |
| GET | `/health` | Returns backend health status. |

## Evaluation results

RAGAS evaluation metrics on test queries against the Anis Shaikh resume:

| Metric | Score |
| --- | --- |
| Faithfulness | 0.67 |
| Answer relevancy | 0.93 |
| Context precision | 0.67 |

**How to run evaluation:**

1. Ensure all dependencies are installed:
   ```bash
   pip install -r backend/requirements.txt
   pip install ragas datasets
   ```

2. Start the backend server:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

3. Run evaluation:
   ```bash
   cd backend
   python eval.py
   ```

**Metric definitions:**
- **Faithfulness**: How factually accurate the generated answers are to the source context
- **Answer Relevancy**: How relevant the answers are to the questions asked
- **Context Precision**: How well the retrieval system finds relevant document chunks

