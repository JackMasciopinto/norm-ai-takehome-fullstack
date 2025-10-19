"""
Simple test to exercise the query functionality with laws.pdf
"""
from app.utils import DocumentService, QdrantService

def test_query_functionality():
    print("🚀 Starting test...")
    
    # Step 1: Load and parse PDF
    print("\n📄 Step 1: Parsing PDF...")
    file_path = "docs/laws.pdf"
    doc_service = DocumentService(file_path=file_path)
    docs = doc_service.create_documents()
    print(f"✅ Extracted {len(docs)} documents")
    
    # Print first few sections
    print("\n📋 First 3 sections:")
    for i, doc in enumerate(docs[:3]):
        print(f"  - {doc.metadata['Section']}: {doc.text}")
    
    # Step 2: Initialize vector store
    print("\n🔗 Step 2: Connecting to Qdrant...")
    qdrant = QdrantService(k=3)
    qdrant.connect()
    print("✅ Connected")
    
    # Step 3: Load documents
    print("\n📥 Step 3: Loading documents into vector store...")
    qdrant.load(docs)
    print("✅ Documents loaded")
    
    # Step 4: Test queries
    print("\n🔍 Step 4: Testing queries...\n")
    
    test_queries = [
        "What happens if I steal?",
        "What are the penalties for theft?",
        "What laws relate to punishment?"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}")
        
        output = qdrant.query(query)
        
        print(f"\n💬 Response:\n{output.response}\n")
        print(f"📚 Citations ({len(output.citations)}):")
        for citation in output.citations:
            print(f"\n  Source: {citation.source}")
            print(f"  Text: {citation.text}")
    
    print("\n\n✨ Test completed successfully!")

if __name__ == "__main__":
    test_query_functionality()

