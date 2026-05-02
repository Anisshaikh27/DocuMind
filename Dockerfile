# ── Stage 1: Build React frontend ─────────────────────────────────────────────
FROM node:20-slim AS frontend-builder

WORKDIR /frontend
COPY frontend/DocuMind/package*.json ./
RUN npm ci --omit=dev

COPY frontend/DocuMind/ ./
# Build with production API URL pointing to the same origin (relative)
RUN npm run build

# ── Stage 2: Python backend (CPU-only, lean) ───────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Install CPU-only PyTorch first (much smaller than default CUDA build)
RUN pip install --no-cache-dir \
    torch==2.2.2+cpu torchvision==0.17.2+cpu \
    --extra-index-url https://download.pytorch.org/whl/cpu

# Install remaining backend dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the embedding model so runtime startup is instant
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy backend source
COPY backend/ ./

# Copy the compiled React app into a 'static' folder served by FastAPI
COPY --from=frontend-builder /frontend/dist ./static

# Hugging Face Spaces requires port 7860
EXPOSE 7860

# Create a non-root user (HF Spaces best practice)
RUN useradd -m appuser && chown -R appuser /app
USER appuser

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
