import os
import chromadb
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv

load_dotenv(override=True)

CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "professor_reviews"
TOP_K = 5

# Load embedding model and ChromaDB
print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

print("Connecting to ChromaDB...")
client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = client.get_collection(COLLECTION_NAME)

# Load Groq client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def retrieve(query, k=TOP_K):
    """Retrieve top-k relevant chunks for a query."""
    query_embedding = model.encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=k,
        include=["documents", "metadatas", "distances"]
    )
    chunks = []
    for i in range(len(results["documents"][0])):
        chunks.append({
            "text": results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "distance": results["distances"][0][i]
        })
    return chunks


def generate(query, chunks):
    """Generate a grounded answer using retrieved chunks."""
    context = "\n\n".join(
        f"[Source: {c['source']}]\n{c['text']}" for c in chunks
    )

    prompt = f"""You are a helpful assistant that answers questions about CS professors at Queens College, CUNY.

Answer the question using ONLY the information provided in the documents below.
Do not use any outside knowledge. If the documents do not contain enough information to answer the question, say exactly: "I don't have enough information in my documents to answer that."

Documents:
{context}

Question: {query}

Answer:"""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.2
    )
    return response.choices[0].message.content


def ask(query):
    """Full pipeline: retrieve + generate."""
    if not query.strip():
        return "Please enter a question.", ""

    chunks = retrieve(query)
    answer = generate(query, chunks)
    sources = list(dict.fromkeys(c["source"] for c in chunks))  # deduplicated
    sources_text = "\n".join(f"• {s}" for s in sources)
    return answer, sources_text


# Gradio UI
import gradio as gr

with gr.Blocks(title="Queens College CS Professor Guide") as demo:
    gr.Markdown("# 🎓 Queens College CS — Unofficial Professor Guide")
    gr.Markdown("Ask anything about CS professors at Queens College, CUNY based on student reviews.")

    with gr.Row():
        inp = gr.Textbox(
            label="Your question",
            placeholder="e.g. Which professor is best for beginners?",
            lines=2
        )

    btn = gr.Button("Ask", variant="primary")

    with gr.Row():
        answer_box = gr.Textbox(label="Answer", lines=8)
        sources_box = gr.Textbox(label="Retrieved from", lines=8)

    btn.click(ask, inputs=inp, outputs=[answer_box, sources_box])
    inp.submit(ask, inputs=inp, outputs=[answer_box, sources_box])

if __name__ == "__main__":
    print("Starting app at http://localhost:7860")
    demo.launch()
