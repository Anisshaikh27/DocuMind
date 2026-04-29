import json
import os
from pathlib import Path


INSTALL_MESSAGE = (
    "Missing evaluation dependency. Install it with:\n"
    "pip install ragas datasets\n"
    "or from this project root:\n"
    "pip install -r requirements.txt"
)


try:
    from datasets import Dataset
    from dotenv import load_dotenv
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_openai import ChatOpenAI
    from ragas import evaluate
    from ragas.embeddings import LangchainEmbeddingsWrapper
    from ragas.llms import LangchainLLMWrapper
    from ragas.metrics import answer_relevancy, context_precision, faithfulness
except ImportError as exc:
    raise SystemExit(f"{INSTALL_MESSAGE}\n\nOriginal error: {exc}") from exc

from retrieval import answer


load_dotenv(Path(__file__).resolve().parent.parent / ".env")

TEST_DATASET = [
    {
        "question": "What is Anis Shaikh's current education?",
        "ground_truth": "Anis Shaikh is pursuing a B.Tech in Artificial Intelligence and Data Science at AISSMS IOIT, Pune, from 2022 to present, with a CGPA of 8.23/10.",
    },
    {
        "question": "What technologies were used to build DocuMind?",
        "ground_truth": "DocuMind uses Python, LangChain, FAISS, Anthropic API, React, and FastAPI.",
    },
    {
        "question": "What did Anis do during the Machine Learning Intern role at AI Adventures?",
        "ground_truth": "At AI Adventures, Anis built and deployed ML pipelines with web scraping, data validation using pytest/flake8, model training on high-dimensional data, AWS EC2 deployment, GitHub Actions CI/CD, and a Flask REST API.",
    },
]


def build_eval_dataset() -> Dataset:
    rows = {
        "question": [],
        "answer": [],
        "contexts": [],
        "ground_truth": [],
    }

    for item in TEST_DATASET:
        result = answer(item["question"])

        rows["question"].append(item["question"])
        rows["answer"].append(result.get("answer", ""))
        rows["contexts"].append(result.get("sources", []))
        rows["ground_truth"].append(item["ground_truth"])

    return Dataset.from_dict(rows)


def print_results_table(results_dict: dict) -> None:
    metric_names = ["faithfulness", "answer_relevancy", "context_precision"]

    print("\nRAGAS Evaluation Results")
    print("-" * 36)
    print(f"{'Metric':<24}Score")
    print("-" * 36)

    for metric in metric_names:
        score = results_dict.get(metric)
        if isinstance(score, (int, float)):
            print(f"{metric:<24}{score:.4f}")
        else:
            print(f"{metric:<24}{score}")

    print("-" * 36)


def build_ragas_evaluators():
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        raise RuntimeError("GROQ_API_KEY is missing. Add it to your .env file before running evaluation.")

    evaluator_llm = LangchainLLMWrapper(
        ChatOpenAI(
            model="openai/gpt-oss-20b",
            api_key=groq_api_key,
            base_url="https://api.groq.com/openai/v1",
        )
    )
    evaluator_embeddings = LangchainEmbeddingsWrapper(
        HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"local_files_only": True},
        )
    )

    return evaluator_llm, evaluator_embeddings


def main() -> None:
    dataset = build_eval_dataset()
    evaluator_llm, evaluator_embeddings = build_ragas_evaluators()
    results = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy, context_precision],
        llm=evaluator_llm,
        embeddings=evaluator_embeddings,
    )
    results_dict = results.to_pandas().mean(numeric_only=True).to_dict()

    print_results_table(results_dict)

    with open("eval_results.json", "w", encoding="utf-8") as f:
        json.dump(results_dict, f, indent=2)


if __name__ == "__main__":
    main()
