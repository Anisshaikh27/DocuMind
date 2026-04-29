import os
import json

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts text from all pages of a PDF file.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        str: Concatenated text from all pages.

    Raises:
        FileNotFoundError: If the file does not exist.
    """

    # Check if file exists
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found at path: {pdf_path}")

    from PyPDF2 import PdfReader

    # Read PDF
    reader = PdfReader(pdf_path)
    pages_text = []

    # Extract text from each page
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages_text.append(text.strip())

    # Join pages with newline and clean extra whitespace
    full_text = "\n".join(pages_text)
    return " ".join(full_text.split())

# if __name__=="__main__":
#     pdf_path = r"C:\Users\SHREE\Downloads\scorereport.pdf"
#     extracted_text = extract_text_from_pdf(pdf_path)
    
#     with open("scorereport.txt", "w") as f:
#         f.write(extracted_text)

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Splits text into chunks using LangChain's RecursiveCharacterTextSplitter.

    Args:
        text (str): Input text to split.
        chunk_size (int): Maximum size of each chunk (in characters).
        overlap (int): Overlap between chunks (in characters).

    Returns:
        list[str]: List of filtered text chunks (>= 30 characters).
    """

    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
    except ImportError:
        from langchain.text_splitter import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ". ", " "]
    )

    chunks = splitter.split_text(text)

    # Filter out chunks shorter than 30 characters
    return [chunk.strip() for chunk in chunks if chunk and len(chunk.strip()) >= 30]




# Module-level variable (lazy-loaded)
_model = None

def generate_embeddings(chunks: list[str]) -> list[list[float]]:
    """
    Generates embeddings for a list of text chunks using SentenceTransformer.

    Args:
        chunks (list[str]): List of text chunks.

    Returns:
        list[list[float]]: List of embeddings (each embedding is a list of floats).
    """
    global _model

    # Handle empty input
    if not chunks:
        return []

    # Lazy load the model (only once)
    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer("all-MiniLM-L6-v2")

    # Generate embeddings
    embeddings = _model.encode(chunks, show_progress_bar=False)

    # Convert to plain Python list of lists
    return embeddings.tolist()


def build_and_save_index(
    chunks: list[str],
    embeddings: list[list[float]],
    save_dir: str = "faiss_index",
) -> dict:
    """
    Builds a FAISS IndexFlatL2 from embeddings and saves the index + chunks.
    """
    if len(chunks) != len(embeddings):
        raise ValueError("Chunks and embeddings must have the same length.")

    if not chunks:
        raise ValueError("Chunks list is empty.")

    os.makedirs(save_dir, exist_ok=True)

    import faiss
    import numpy as np

    embeddings_np = np.array(embeddings).astype("float32")
    dimension = embeddings_np.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings_np)

    faiss.write_index(index, os.path.join(save_dir, "index.faiss"))

    with open(os.path.join(save_dir, "chunks.json"), "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    return {"index_size": len(chunks), "save_dir": save_dir}


def load_index(save_dir: str = "faiss_index") -> tuple[object, list[str]]:
    """
    Loads a FAISS index and corresponding chunks.
    """
    if not os.path.exists(save_dir):
        raise FileNotFoundError(f"Directory not found: {save_dir}")

    index_path = os.path.join(save_dir, "index.faiss")
    chunks_path = os.path.join(save_dir, "chunks.json")

    if not os.path.exists(index_path) or not os.path.exists(chunks_path):
        raise FileNotFoundError(f"Required files not found in directory: {save_dir}")

    import faiss

    index = faiss.read_index(index_path)

    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    return index, chunks


def ingest_document(pdf_path: str) -> dict:
    """
    Runs the full PDF ingestion pipeline and saves a FAISS index.
    """
    try:
        text = extract_text_from_pdf(pdf_path)
        chunks = chunk_text(text)
        embeddings = generate_embeddings(chunks)
        build_and_save_index(chunks, embeddings)

        return {
            "chunks": len(chunks),
            "status": "success",
            "index_path": "faiss_index/",
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
        }
