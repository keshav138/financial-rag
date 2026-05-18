from app.rag.chain import query_rag

result = query_rag('what are the main risk factors')

print("Answer: ", result['answer'])

print('\nSources')

for s in result['sources']:
    print(f'Page {s["page"]} : {s["content"][:100]}')