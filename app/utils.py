from pydantic import BaseModel, Field
from app.base_legal_doc import LawsDocument
import qdrant_client
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.llms.openai import OpenAI
from llama_index.core.query_engine import CitationQueryEngine
import json
from llama_index.core.schema import Document
from dataclasses import dataclass
from typing import Optional
import os
import re
import fitz  # PyMuPDF
from llama_cloud_services import LlamaExtract

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
    """Extract laws from a PDF using LlamaExtract and return LlamaIndex Documents."""
    
    def __init__(self):
        self.extractor = LlamaExtract(api_key=key)
        try:
            print( "Trying to get existing agent..." )
            self.agent = self.extractor.get_agent(name="Law Agent")
        except:
            self.agent = self.extractor.create_agent(data_schema=LawsDocument, name="Law Agent")

    def process_section_recursively(self, section_data):
            """Recursively process sections and all nested subsections."""
            section_text = section_data.pop('text', '')
            if section_text:
                doc = Document(
                    text=section_text,
                    metadata={
                        **section_data,
                    }
                )
                self.documents.append(doc)
            
            subsections = section_data.get('subsections', [])
            if subsections:
                for subsection in subsections:
                    self.process_section_recursively(subsection)

    def build_documents(self, file_path: str, laws_data: LawsDocument) -> list[Document]:
        """
        Wrapper to create documents from a PDF file.
        """
        self.documents = []
        for law_category in laws_data['laws']:
            for section in law_category['sections']:
                self.process_section_recursively(section)

        return self.documents

    def create_documents(self, file_path: str) -> list[Document]:
        """
        Parse PDF and extract structured legal sections using LlamaExtract.
        Converts the hierarchical structure into flat documents for vector search.
        """
        # Use LlamaExtract to extract structured data from PDF
        extraction_result = self.agent.extract(file_path)

        
        # Convert structured data to flat documents
        documents = self.build_documents(file_path=file_path, laws_data=extraction_result.data)
        
        return documents
            
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
    
    def connect(self, collection_name: str = 'temp') -> None:
        # Configure global Settings (replaces ServiceContext)
        Settings.embed_model = OpenAIEmbedding(api_key=openai_key)
        Settings.llm = OpenAI(api_key=openai_key, model="gpt-4")
        
        # Create Qdrant client and vector store
        client = qdrant_client.QdrantClient(location=":memory:")
        vstore = QdrantVectorStore(client=client, collection_name=collection_name)

        # Create index from vector store
        self.index = VectorStoreIndex.from_vector_store(vector_store=vstore)

    def load(self, docs = list[Document]):
        self.index.insert_nodes(docs)
    
    def clean_text(self, text: str) -> str:
        """
        Clean citation text by removing "Source X:" prefixes.
        """
        return re.sub(r'Source \d+:', '', text)

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
                    source=node.metadata.get("section", "N/A"),
                    text=self.clean_text(node.text)
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





