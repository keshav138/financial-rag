from app.rag.loader import load_and_chunk_pdf
from app.rag.vectorstore import ingest_chunks, get_retriever

chunks = load_and_chunk_pdf(r"")
count = ingest_chunks(chunks)

print(f"Ingested {count} chunks")

retriever = get_retriever(k=3)
results = retriever.invoke('what are the main risk factors')

for i, doc in enumerate(results):
    print(f'\n--- Chunks {i+1} page {doc.metadata.get("page")}----')
    print(doc.page_content[:300])