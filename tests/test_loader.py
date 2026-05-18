from app.rag.loader import load_and_chunk_pdf

chunks = load_and_chunk_pdf(r'')


print(f'Total Chunks: ', {len(chunks)})
print(f'\nFirst chunk:\n{chunks[0].page_content}')
print(f'\n Metadata \n {chunks[0].metadata}')