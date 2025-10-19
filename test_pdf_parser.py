"""
Test script for extract_laws_from_pdf function
Tests the PDF parsing functionality using LlamaParse with LLM-based extraction
"""
from app.utils import DocumentService


def test_extract_laws():
    """Test extracting laws from the PDF file"""
    print("Testing PDF law extraction with LlamaParse...")
    
    pdf_path = "docs/laws.pdf"
    print(f"Parsing: {pdf_path}\n")
    
    try:
        docs = DocumentService(file_path=pdf_path).create_documents()
        
        # Verify we got documents
        assert len(docs) > 0, "Should have extracted at least one document"
        print(f"Extracted {len(docs)} law documents\n")
        print("=" * 80)
        
        # Display extracted LlamaParse documents directly
        for i, doc in enumerate(docs, 1):
            print(f"\nDOCUMENT {i}")
            print(f"Section: {doc.metadata.get('Section', 'N/A')}")
            print("-" * 80)
            print(doc.text)
            print("=" * 80)
        
        return docs
        
    except FileNotFoundError:
        print(f"Error: PDF file not found at {pdf_path}")
        return None
    except Exception as e:
        print(f"Error extracting laws: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    docs = test_extract_laws()
    if docs:
        print(f"\n\nTotal: {len(docs)} documents extracted")