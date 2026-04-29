import os
from pathlib import Path

from dotenv import load_dotenv
from openai import APIError, OpenAI, OpenAIError

from ingestion import load_index


load_dotenv(Path(__file__).resolve().parent.parent / ".env")

_model = None


def search_index(query: str, faiss_index, chunks: list[str], top_k: int = 3) -> list[str]:
    """
    Searches the FAISS index using a query and returns top_k matching chunks.
    """
    global _model

    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer("all-MiniLM-L6-v2")

    import numpy as np

    query_embedding = _model.encode([query], show_progress_bar=False)
    query_vec = np.array(query_embedding).astype("float32").reshape(1, -1)

    _, indices = faiss_index.search(query_vec, top_k)

    results = []
    for idx in indices[0]:
        if idx != -1 and 0 <= idx < len(chunks):
            results.append(chunks[idx])

    return results


def build_prompt(context_chunks: list[str], question: str) -> str:
    """
    Builds a structured prompt with instructions, retrieved context, and question.
    """
    system_instruction = (
        "You are a document assistant that answers questions ONLY using the provided context. "
        "Do not use outside knowledge or make assumptions. "
        "If the answer is not present in the context, say: "
        '"I cannot find that information in the document." '
        "Always cite which context section (e.g., Context [1]) supports your answer. "
        "Keep your response clear and concise."
    )

    context_text = ""
    for i, chunk in enumerate(context_chunks, start=1):
        context_text += f"Context [{i}]: {chunk}\n"

    return f"{system_instruction}\n\n{context_text}\nQuestion: {question}"


def query_llm(
    prompt: str,
    model: str = "openai/gpt-oss-20b",
    max_tokens: int = 512,
) -> str:
    try:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            return "LLM error: GROQ_API_KEY is not set in the environment."

        client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=api_key,
        )

        response = client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except (APIError, OpenAIError) as e:
        return "LLM error: " + str(e)


def is_relevant(query_embedding, chunk_embeddings, threshold: float = 0.3) -> bool:
    import numpy as np

    query_vector = np.array(query_embedding, dtype="float32")
    chunk_vectors = np.array(chunk_embeddings, dtype="float32")

    if chunk_vectors.size == 0:
        return False

    query_norm = np.linalg.norm(query_vector)
    chunk_norms = np.linalg.norm(chunk_vectors, axis=1)

    if query_norm == 0:
        return False

    denominator = query_norm * chunk_norms
    valid = denominator > 0

    if not np.any(valid):
        return False

    similarities = np.full(chunk_vectors.shape[0], -1.0, dtype="float32")
    similarities[valid] = np.dot(chunk_vectors[valid], query_vector) / denominator[valid]

    return float(np.max(similarities)) > threshold


def answer(question: str) -> dict:
    """
    Answers a question using the indexed document chunks.
    """
    import numpy as np

    try:
        faiss_index, chunks = load_index(Path(__file__).resolve().parent / "faiss_index")
    except FileNotFoundError:
        return {
            "answer": "No document indexed yet.",
            "sources": [],
            "question": question,
        }

    global _model

    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer("all-MiniLM-L6-v2")

    query_embedding = _model.encode([question], show_progress_bar=False)[0]
    query_vec = np.array(query_embedding, dtype="float32").reshape(1, -1)
    chunk_embeddings = np.array(
        [faiss_index.reconstruct(i) for i in range(faiss_index.ntotal)],
        dtype="float32",
    )

    if not is_relevant(query_embedding, chunk_embeddings):
        return {
            "answer": (
                "I could not find relevant information about this in the uploaded document. "
                "Please try rephrasing or upload a more relevant document."
            ),
            "sources": [],
            "question": question,
        }

    _, indices = faiss_index.search(query_vec, 3)
    retrieved_chunks = []
    for idx in indices[0]:
        if idx != -1 and 0 <= idx < len(chunks):
            retrieved_chunks.append(chunks[idx])

    prompt = build_prompt(retrieved_chunks, question)
    answer_text = query_llm(prompt)

    return {
        "answer": answer_text,
        "sources": retrieved_chunks,
        "question": question,
    }
