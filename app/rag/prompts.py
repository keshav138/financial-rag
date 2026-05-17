from langchain_core.prompts import PromptTemplate

RAG_PROMPT = PromptTemplate(
    input_variable=['context', 'question'],
    template="""
    You are a financial analyst assistant. Answer the question using ONLY the context provided below.
    If the answer is not in the context, say 'I cannot find this information in the provided document.
    Do not make up numbers, dates or financial figures.
    
    Context : {context}
    
    Question : {question}
    
    Answer:
    """
)