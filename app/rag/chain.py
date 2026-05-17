from langchain_groq import ChatGroq
from langchain_core.runnables import RunnablePassthrough # sort of a placeholder, keeps the value it recieves as it is
from langchain_core.output_parsers import StrOutputParser # llm returns a ai_object, this parses it as a raw string
from app.rag.vectorstore import get_retriever
from app.rag.prompts import RAG_PROMPT

import os
from dotenv import load_dotenv

load_dotenv()

def get_llm():
    """
    Function to fetch llm object
    """
    
    return ChatGroq(
        api_key = os.getenv('GROQ_API_KEY'),
        model = 'llama-3.1-8b-instant',
        temperature = 0.1, # remains factual
        max_tokens = 1024
    )
    

def format_docs(docs) -> str:
    """
    Joins returned docs by ChromaDB and joins them into one cohesive string
    """
    
    return "\n\n".join(doc.page_content for doc in docs)


def get_rag_chain():
    llm = get_llm()
    retriever = get_retriever(k=5)
    
    """
    this is just a created object, a blueprint, a single value when passed will go the first one's first, the dictonary, both to question and context
    both get a copy of the question
    """
    
    # this is LCEL (Langchain expression language, using |)
    chain = (
        {
            "question":RunnablePassthrough(),
            "context": retriever | format_docs
        }
        | RAG_PROMPT
        | llm
        | StrOutputParser()
    )
    
    return chain, retriever


def query_rag(question: str) -> dict:
    
    chain, retriever = get_rag_chain()
    
    # one call to get context, because the llm output strips everything, only keeps answer
    source_docs = retriever.invoke(question)
    
    # one call to get the output
    answer  = chain.invoke(question)
    
    sources = [
        {
            'page' : doc.metadata.get('page'),
            'content': doc.page_content[:200]
        } 
        for doc in source_docs
    ]
    
    return {
        "answer" : answer,
        "sources" : sources
    }
    
    

    