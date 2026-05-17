from prometheus_client import Counter, Histogram # prebuilt metrics along with gauge, summary
from prometheus_fastapi_instrumentator import Instrumentator # library that automates metrics for all endpoints


# 4 global metrics trackers

RAG_LATENCY = Histogram(
    name='rag_inference_latency_seconds',
    documentation='Time taken for a RAG chain to return an answer',
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 30.0]
)

RAG_REQUESTS_TOTAL = Counter(
    name='rag_requests_total',
    documentation='Total number of rag queries made'
)

RAG_FAILED_REQUESTS = Counter(
    name='rag_failed_total_requests',
    documentation='Total number of failed RAG queries'
)

DOCUMENTS_INGESTED = Counter(
    name='documents_ingested_total',
    documentation='Total numbers of document chunks ingested into ChromeDB'
)

def setup_instrumentator(app):
    """
    Sets up automatic HTTP metrics on all endpoints
    Exposes /metrics endpoint for prometheus to scrape from
    """
    
    Instrumentator(
        should_group_status_codes=True, # groups HTTP requests in the hundreds , 2XX, 3XX, 4XX, 5XX
        should_ignore_untemplated=True, # client hits a unknown endpoint, dont track that
        should_respect_env_var=True, # 
        should_instrument_requests_inprogress=True, # currently actively hanging requests
        excluded_handlers=['/metrics', '/health'] # ignore endpoints
    ).instrument(app).expose(app) # .instrument attaches middleware to track http requests, .expose creates a /metrics endpoint
    