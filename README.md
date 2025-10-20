# Norm AI Legal Query System

A fullstack application that allows users to query Game of Thrones laws using AI-powered semantic search with citations.

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Environment variables: `OPENAI_API_KEY` and `LLAMA_CLOUD_KEY`

### Run with Docker Compose (Recommended)
```bash
# Set your API keys
export OPENAI_API_KEY="your-openai-key"
export LLAMA_CLOUD_KEY="your-llama-cloud-key"

# Start both frontend and backend
docker-compose up
```

**Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

### Alternative: Run Separately

**Backend only:**
```bash
docker build -t norm-ai-app .
docker run -p 8000:80 \
  -e OPENAI_API_KEY="your-key" \
  -e LLAMA_CLOUD_KEY="your-key" \
  norm-ai-app
```

**Frontend only:**
```bash
cd frontend
npm install
npm run dev
```

## Usage
1. Open http://localhost:3000
2. Enter a legal query (e.g., "What happens if I steal from the Sept?")
3. View AI-generated responses with source citations

## Architecture
- **Backend**: FastAPI with Qdrant vector search and OpenAI
- **Frontend**: Next.js with TypeScript
- **Data**: Game of Thrones laws PDF processed via LlamaExtract


## Design Decisions
- **Database** For simplicity no database vector store included/using in memory version, in a live app this would be a real db
- **Document Loading** The document is loaded when the app starts up, each time it is deployed. In a live app there would be a separate documents endpoint for inputting documents
- **Documents Structure** The document is extracted into a general structure of sections/subsections to be flexible for future uses. If specific fields or structure were needed the extract function could be prompted with an arbitrary JSON or extend off of the existing base_legal_doc.py. Very likely becoming a database object given the potential variety required.
