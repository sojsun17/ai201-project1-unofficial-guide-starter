from sentence_transformers import SentenceTransformer
import chromadb

model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_collection("professor_reviews")

query = "How difficult are Professor Telang exams?"
embedding = model.encode([query]).tolist()
results = collection.query(query_embeddings=embedding, n_results=3, include=["documents","metadatas","distances"])

for i in range(3):
    print("Source:", results["metadatas"][0][i]["source"])
    print("Distance:", round(results["distances"][0][i], 4))
    print("Text:", results["documents"][0][i][:200])
    print()
