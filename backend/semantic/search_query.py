import os
import json
import openai
import numpy as np
from dotenv import load_dotenv
from pathlib import Path
from typing import List, Dict

# Load API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

INDEX_FILE = Path(__file__).resolve().parent / "vector_index.json"

# Get query embedding
def get_query_embedding(query: str) -> List[float]:
    response = openai.embeddings.create(
        model="text-embedding-ada-002",
        input=query
    )
    return response.data[0].embedding

# Load vector index
def load_vector_index() -> List[Dict]:
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# Cosine similarity
def cosine_similarity(vec1, vec2) -> float:
    a = np.array(vec1)
    b = np.array(vec2)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Main RAG search
def semantic_answer(query: str, top_k: int = 3) -> Dict:
    query_vec = get_query_embedding(query)
    index = load_vector_index()

    # Sort matches
    scored = []
    for item in index:
        sim = cosine_similarity(query_vec, item["embedding"])
        scored.append((item["text"], item["source"], sim))
    scored.sort(key=lambda x: x[2], reverse=True)

    top_matches = scored[:top_k]
    context = "\n\n".join([match[0] for match in top_matches])
    sources = [match[1] for match in top_matches]

    # Call GPT-4 with RAG prompt
    prompt = f"""You are an intelligent meeting assistant. Use the following meeting transcripts to answer the question.

Meeting Excerpts:
{context}

Question: {query}
Answer:"""

    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        final_answer = response.choices[0].message.content
    except Exception as e:
        final_answer = f"❌ GPT failed: {e}"

    return {
        "answer": final_answer,
        "sources": sources
    }

# Optional CLI
if __name__ == "__main__":
    q = input("🔎 Enter your question: ")
    result = semantic_answer(q)
    print("\n🧠 Answer:\n", result["answer"])
    print("\n📂 Sources:")
    for s in result["sources"]:
        print("–", s)
