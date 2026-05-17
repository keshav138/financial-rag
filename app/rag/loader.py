from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import tempfile
import os

def load_and_chunk_pdf(file_path: str) -> list:
    """
    Loads a PDF from a file path, splits into chunks.
    Returns list of langchain documents objects.
    """
    
    loader = PyPDFLoader(file_path)  # this is the the setup
    documents = loader.load()  # this implements it, extracting data per page
    
    # this is again a setup func.
    splitter = RecursiveCharacterTextSplitter(  
        chunk_size = 1000, ## approx 200-250 words
        chunk_overlap = 200,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    
    # this splits as per configured into langchain chunks/documents
    chunks = splitter.split_documents(documents)
    
    return chunks


def load_chunks_from_bytes(file_bytes: bytes, filename: str) -> list:
    """
    For FastAPI file uploads - write to a temp file first then loads
    """
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
    
    try:
        chunks = load_and_chunk_pdf(tmp_path)
    finally:
        os.unlink(tmp_path) ## temp file cleanup
        
    return chunks
    
        
    
    
