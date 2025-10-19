from pydantic import BaseModel
import qdrant_client
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_cloud_services import LlamaParse
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.llms.openai import OpenAI
from llama_index.core.query_engine import CitationQueryEngine
import json
from llama_index.core.schema import Document
from dataclasses import dataclass
import os
import fitz  # PyMuPDF

key = os.environ['LLAMA_CLOUD_KEY']
openai_key = os.environ['OPENAI_API_KEY']

@dataclass
class Input:
    query: str
    file_path: str

@dataclass
class Citation:
    source: str
    text: str

class Output(BaseModel):
    query: str
    response: str
    citations: list[Citation]

class DocumentService:
    """Extract laws from a PDF and return LlamaIndex Documents."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.llm = OpenAI(api_key=openai_key, model="gpt-4")

    def parse_pdf(self) -> list[Document]:
        """
        Parse PDF and extract structured legal sections.
        Uses LlamaParse for intelligent PDF extraction and GPT for section identification.
        """
        parser = LlamaParse(api_key=key, result_type="text")
        documents = parser.load_data(self.file_path)
        return "\n".join([doc.text for doc in documents])
    
    def extract_sections(self, full_text: str) -> list[Document]:
        """
        Extract sections from the full text of the PDF.
        Uses GPT for section identification.
        """
        prompt = f"""You are analyzing a legal document. Extract each distinct legal section/law from the text below.
        
                    Legal documents typically have numbered sections like:
                    - 1, 2, 3 (main sections)
                    - 1.1, 1.2, 2.1, 2.2 (subsections)
                    - Or similar hierarchical numbering

                    For each section found, return ONLY a JSON array with objects containing:
                    - "section_id": The section number (e.g., "1", "1.1", "2")
                    - "text": The complete text of that section

                    Return ONLY the JSON array, no other text. If no clear sections are found, break the document into logical paragraphs or segments.

                    Document text:
                    {full_text}"""
        response = self.llm.complete(prompt)
        response_text = response.text.strip()
        sections = json.loads(response_text)
        return sections
    
    def create_documents(self) -> list[Document]:
        """
        Parse PDF and extract structured legal sections.
        Uses LlamaParse for intelligent PDF extraction and GPT for section identification.
        """
        full_text = self.parse_pdf()
        sections = self.extract_sections(full_text=full_text)
        docs = [Document(metadata={"Section": f"Law {section['section_id']}"}, text=section['text']) for section in sections]
        return docs
            
class QdrantService:
    def __init__(self, k: int = 3):
        """
        Initialize QdrantService.
        
        Args:
            k: Number of most similar chunks to retrieve (default 3).
               Higher k helps capture cross-references between laws.
        """
        self.index = None
        self.k = k
    
    def connect(self) -> None:
        # Configure global Settings (replaces ServiceContext)
        Settings.embed_model = OpenAIEmbedding(api_key=openai_key)
        Settings.llm = OpenAI(api_key=openai_key, model="gpt-4")
        
        # Create Qdrant client and vector store
        client = qdrant_client.QdrantClient(location=":memory:")
        vstore = QdrantVectorStore(client=client, collection_name='temp')

        # Create index from vector store
        self.index = VectorStoreIndex.from_vector_store(vector_store=vstore)

    def load(self, docs = list[Document]):
        self.index.insert_nodes(docs)
    
    def query(self, query_str: str) -> Output:
        """
        This method needs to initialize the query engine, run the query, and return
        the result as a pydantic Output class. This is what will be returned as
        JSON via the FastAPI endpount. Fee free to do this however you'd like, but
        a its worth noting that the llama-index package has a CitationQueryEngine...

        Also, be sure to make use of self.k (the number of vectors to return based
        on semantic similarity).

        # Example output object
        citations = [
            Citation(source="Law 1", text="Theft is punishable by hanging"),
            Citation(source="Law 2", text="Tax evasion is punishable by banishment."),
        ]

        output = Output(
            query=query_str, 
            response=response_text, 
            citations=citations
            )
        
        return output
        """
        
        # Initialize CitationQueryEngine with similarity_top_k
        query_engine = CitationQueryEngine.from_args(
            self.index,
            similarity_top_k=self.k,
            citation_chunk_size=768  # Larger chunks capture more context for cross-references
        )
        
        # Run the query
        response = query_engine.query(query_str)
        
        # Extract citations from response
        citations = []
        if hasattr(response, 'source_nodes'):
            for node in response.source_nodes:
                citation = Citation(
                    source=node.metadata.get("Section", "Unknown"),
                    text=node.text
                )
                citations.append(citation)
        
        # Create and return Output object
        output = Output(
            query=query_str,
            response=str(response),
            citations=citations
        )
        
        return output

if __name__ == "__main__":
    # Example workflow
    file_path = "docs/laws.pdf"
    
    doc_service = DocumentService(file_path=file_path)
    docs = doc_service.create_documents()

    qdrant = QdrantService(k=3)
    qdrant.connect()
    qdrant.load(docs)

    output = qdrant.query("what happens if I steal?")
    print(output)





