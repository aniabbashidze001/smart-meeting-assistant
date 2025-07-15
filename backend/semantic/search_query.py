import json
import os
from pathlib import Path
from typing import Dict, List

import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

INDEX_FILE = Path(__file__).resolve().parent / "vector_index.json"


def get_query_embedding(query: str) -> List[float]:
    """Generate a semantic embedding for the given query string using OpenAI's embedding model."""
    response = client.embeddings.create(model="text-embedding-ada-002", input=query)
    return response.data[0].embedding


def load_vector_index() -> List[Dict]:
    """Load the vector index from the `vector_index.json` file."""
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def cosine_similarity(vec1, vec2) -> float:
    """Calculate the cosine similarity between two vectors."""
    a = np.array(vec1)
    b = np.array(vec2)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def semantic_answer(query: str, top_k: int = 3) -> Dict:
    """
        Generate a semantic answer to a query by finding the most relevant
        meeting transcript excerpts based on cosine similarity and GPT response.

        Args:
            query (str): The question or query to answer.
            top_k (int): Number of top matching excerpts to include in the context.

        Returns:
            Dict: A dictionary containing the generated answer and the sources used.
    """
    query_vec = get_query_embedding(query)
    index = load_vector_index()

    scored = []
    for item in index:
        sim = cosine_similarity(query_vec, item["embedding"])
        scored.append((item["text"], item["source"], sim))
    scored.sort(key=lambda x: x[2], reverse=True)

    top_matches = scored[:top_k]
    context = "\n\n".join([match[0] for match in top_matches])
    sources = [match[1] for match in top_matches]

    prompt = f"""You are an intelligent meeting assistant. Use the following meeting transcripts to answer the question.

Meeting Excerpts:
{context}

Question: {query}
Answer:"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        final_answer = response.choices[0].message.content
    except Exception as e:
        final_answer = f"❌ GPT failed: {e}"

    return {"answer": final_answer, "sources": sources}


if __name__ == "__main__":
    q = input("🔎 Enter your question: ")
    result = semantic_answer(q)
    print("\n🧠 Answer:\n", result["answer"])
    print("\n📂 Sources:")
    for s in result["sources"]:
        print("–", s)
