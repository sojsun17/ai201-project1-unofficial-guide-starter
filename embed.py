import chromadb
from sentence_transformers import SentenceTransformer
from ingest import load_documents, build_chunks

DOCUMENTS_DIR = "documents"
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "professor_reviews"


def embed_and_store(chunks):
    """Embed all chunks and store them in ChromaDB."""
    print("Loading embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("Connecting to ChromaDB...")
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # Delete existing collection if it exists so we start fresh
    existing = [c.name for c in client.list_collections()]
    if COLLECTION_NAME in existing:
        client.delete_collection(COLLECTION_NAME)
        print("Deleted existing collection.")

    collection = client.create_collection(COLLECTION_NAME)

    print(f"Embedding {len(chunks)} chunks...")
    texts = [chunk["text"] for chunk in chunks]
    sources = [chunk["source"] for chunk in chunks]
    ids = [f"chunk_{i}" for i in range(len(chunks))]

    embeddings = model.encode(texts, show_progress_bar=True)

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings.tolist(),
        metadatas=[{"source": s} for s in sources]
    )

    print(f"\nStored {collection.count()} chunks in ChromaDB at '{CHROMA_DIR}/'")
    return collection


if __name__ == "__main__":
    print("=== Loading and chunking documents ===")
    documents = load_documents(DOCUMENTS_DIR)
    chunks = build_chunks(documents)
    print(f"Total chunks: {len(chunks)}")

    print("\n=== Embedding and storing ===")
    collection = embed_and_store(chunks)

    print("\n=== Quick retrieval test ===")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    test_query = "Which professor is good for beginners?"
    query_embedding = model.encode([test_query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=3,
        include=["documents", "metadatas", "distances"]
    )

    print(f"\nQuery: '{test_query}'")
    for i in range(len(results["documents"][0])):
        print(f"\n--- Result {i+1} ---")
        print(f"Source: {results['metadatas'][0][i]['source']}")
        print(f"Distance: {results['distances'][0][i]:.4f}")
        print(f"Text: {results['documents'][0][i][:200]}...")
