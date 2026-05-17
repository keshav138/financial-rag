from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.rag.loader import load_chunks_from_bytes
from app.rag.vectorstore import ingest_chunks, reset_database
from app.rag.chain import query_rag

from app.monitoring.metrics import(
    setup_instrumentator,
    RAG_LATENCY,
    RAG_FAILED_REQUESTS,
    RAG_REQUESTS_TOTAL,
    DOCUMENTS_INGESTED
)

import time


app = FastAPI(
    title="Financial App RAG",
    description='RAG pipeline over SEC findings',
    version='1.0.0'
)

setup_instrumentator(app)

# ----- Request/Response Model ----- #

class QueryRequest(BaseModel):
    question : str
       
class QueryResponse(BaseModel):
    answer : str
    sources : list
    latency_ms : float

class IngestResponse(BaseModel):
    message : str
    chunks_stored : int
    
    
# --- Endpoints -- #

@app.get('/health')
def health_check():
    return JSONResponse(
        {
            'status' : 'ok'
        }
    )
    

@app.post('/ingest', response_model = IngestResponse)
async def ingest_document(file : UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF's file are supported")

    try:
        file_bytes = await file.read()
        chunks = load_chunks_from_bytes(file_bytes, file.filename)
        count = ingest_chunks(chunks)
        
        DOCUMENTS_INGESTED.inc(count)
        
        return IngestResponse(
            message=f'Successfully ingested {file.filename}',
            chunks_stored = count
        )
        
        
    except Exception as e:
        RAG_FAILED_REQUESTS.inc()
        raise HTTPException(status_code=500, detail = str(e))
    

@app.post('/query', response_model = QueryResponse)
async def query_document(request : QueryRequest):
    if not  request.question.strip():
        return HTTPException(status_code=400, detail='Question cannot be empty.')

    RAG_REQUESTS_TOTAL.inc()

    try:
        start = time.time()
        result = query_rag(request.question)
        latency_ms = time.time() - start
        
        RAG_LATENCY.observe(latency_ms)
        
        return QueryResponse(
            answer = result['answer'],
            sources = result['sources'],
            latency_ms = round(latency_ms * 1000, 2)
        )
        
    except Exception as e:
        RAG_FAILED_REQUESTS.inc()
        raise HTTPException(status_code=500, detail=str(e))
    
    
@app.delete('/reset')
def reset_documents():
    try:
        reset_database()
        return {
            'message' : 'ChromaDB cleared!'
        }
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))
    
    
