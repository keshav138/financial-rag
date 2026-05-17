from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os
from dotenv import load_dotenv


load_dotenv()

CHROMA_PERSIST_DIR = os.getenv("CHROME_PERSIST_DIR", "./chroma_db") # db
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'financial_docs')  # collections name -> sort of table in db

# embeddings runs outside (global scope) loading model is expensive, loads into ram, so loads only once, when server starts up

embeddings = HuggingFaceEmbeddings(
    model_name = 'sentence-transformers/all-MiniLM-L6-v2', # model name, 384 dimension
    model_kwargs={'device':'cpu'}, # as in use the cpu, can also use cuda for gpu
    encode_kwargs={'normalize_embeddings':True} # get values between 0-1
)


def get_vectorstore():
    """
    Database connection
    Returns existing ChromaDB collection or creates a new one
    Persitant-survives restarts
    """
    
    # can call this multiple times
    return Chroma( 
        collection_name = COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_PERSIST_DIR
    )
    
def ingest_chunks(chunks: list[Document]) -> int:
    """
    Embeds existing chunks and stores them into ChromaDB
    Returns number of chunks created.
    """
    
    vectorstore = get_vectorstore()
    
    # handles the embedding and storing, gets vectors, saves vectors + original text+metadata
    # creates 384 vectors per chunk
    vectorstore.add_documents(chunks)
    
    return len(chunks)

def get_retriever(k: int = 5):
    """
    Returns a retriever that fetches up to top-k most relevant chunks
    """
    
    vectorstore = get_vectorstore()
    
    # retriever -> lightweight langchain object, that takes a string, finds doc and returns, no LLM
    return vectorstore.as_retriever(
        search_type='similarity',  # telling ChromaDB to use the default cosine similarity
        search_kwargs={'k': k}
    )
    
def reset_database() -> None:
    """
    Clears the entire ChromaDB database
    """
    
    vectorstore = get_vectorstore()
    vectorstore.delete_collection()
    
    
    

    
    
    
    
    
