import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ingestion import ingest_document
from retrieval import answer


app = FastAPI(title="DocuMind API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/upload")
async def upload(file: UploadFile = File(...)) -> dict:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    upload_path = "/tmp/uploaded.pdf"

    try:
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        contents = await file.read()

        with open(upload_path, "wb") as f:
            f.write(contents)

        result = ingest_document(upload_path)

        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message", "Upload failed."))

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    finally:
        await file.close()


@app.post("/query")
def query(request: QueryRequest) -> dict:
    question = request.question.strip()

    if not question:
        raise HTTPException(status_code=422, detail="Question cannot be empty.")

    try:
        return answer(question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# ── Serve the compiled React frontend ─────────────────────────────────────────
# In production (Docker / HF Spaces) the React build is copied into ./static
_STATIC_DIR = Path(__file__).parent / "static"

if _STATIC_DIR.is_dir():
    # Mount assets (JS, CSS, images) at /assets
    app.mount("/assets", StaticFiles(directory=_STATIC_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_spa(full_path: str) -> FileResponse:
        """Catch-all: return index.html so React Router handles client-side routing."""
        index = _STATIC_DIR / "index.html"
        return FileResponse(index)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=7860, reload=True)
