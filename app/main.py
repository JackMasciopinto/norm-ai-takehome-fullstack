from fastapi import FastAPI, Query, HTTPException
from app.utils import Output, DocumentService, QdrantService
from contextlib import asynccontextmanager

# Global QdrantService instance
qdrant_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load laws.pdf into vector store on startup"""
    global qdrant_service
    
    print("🚀 Starting up... Loading laws.pdf")
    
    # Initialize services
    doc_service = DocumentService()
    qdrant_service = QdrantService(k=3)
    
    # Load and process laws.pdf
    file_path = "docs/laws.pdf"
    print(f"📄 Extracting documents from {file_path}")
    docs = doc_service.create_documents(file_path=file_path)
    print(f"✅ Extracted {len(docs)} documents")
    
    # Connect to vector store and load documents
    print("🔗 Connecting to Qdrant...")
    qdrant_service.connect(collection_name='laws')
    print("✅ Connected")
    
    print("📥 Loading documents into vector store...")
    qdrant_service.load(docs)
    print("✅ Documents loaded - Ready to serve queries!")
    
    yield
    
    # Cleanup on shutdown
    print("👋 Shutting down...")

app = FastAPI(lifespan=lifespan)

@app.get("/query", response_model=Output)
async def query_laws(q: str = Query(..., description="The query string to search for in the laws database")):
    """
    Query the laws database and return relevant information with citations.
    
    Args:
        q: The query string (e.g., "what happens if I steal from the Sept?")
    
    Returns:
        Output: JSON response with query, response text, and citations
    """
    if qdrant_service is None:
        raise HTTPException(status_code=503, detail="Service not initialized yet")
    
    try:
        # Query the vector store
        output = qdrant_service.query(q)
        return output
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "Laws Query API is running",
        "endpoints": {
            "query": "/query?q=<your query here>",
            "docs": "/docs"
        }
    }