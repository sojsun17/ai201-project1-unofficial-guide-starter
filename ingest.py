import os

DOCUMENTS_DIR = "documents"
CHUNK_SIZE = 400
CHUNK_OVERLAP = 50


def load_documents(directory):
    """Load all .txt files from the documents directory."""
    documents = []
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            filepath = os.path.join(directory, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            documents.append({
                "source": filename,
                "text": text
            })
            print(f"Loaded: {filename} ({len(text)} chars)")
    return documents


def clean_text(text):
    """Remove extra whitespace and blank lines."""
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        line = line.strip()
        if line:
            cleaned.append(line)
    return " ".join(cleaned)


def chunk_text(text, source, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Split text into overlapping chunks and tag each with its source."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if len(chunk) > 50:  # skip tiny fragments
            chunks.append({
                "source": source,
                "text": chunk
            })
        start += chunk_size - overlap
    return chunks


def build_chunks(documents):
    """Clean and chunk all loaded documents."""
    all_chunks = []
    for doc in documents:
        cleaned = clean_text(doc["text"])
        chunks = chunk_text(cleaned, doc["source"])
        all_chunks.extend(chunks)
        print(f"  {doc['source']}: {len(chunks)} chunks")
    return all_chunks


if __name__ == "__main__":
    print("=== Loading documents ===")
    documents = load_documents(DOCUMENTS_DIR)
    print(f"\nTotal documents loaded: {len(documents)}")

    print("\n=== Chunking ===")
    chunks = build_chunks(documents)
    print(f"\nTotal chunks: {len(chunks)}")

    print("\n=== Sample chunks (first 5) ===")
    for i, chunk in enumerate(chunks[:5]):
        print(f"\n--- Chunk {i+1} (source: {chunk['source']}) ---")
        print(chunk["text"])
