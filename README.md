# Semantic Chunking RAG System

## Overview

This project implements a **Retrieval-Augmented Generation (RAG) system** that allows users to upload documents and ask questions about them using natural language.

The system processes uploaded documents by performing **semantic chunking**, generating **vector embeddings**, storing them in a **vector database**, and retrieving relevant information to answer user queries using a large language model.

The goal is to improve the accuracy and reliability of responses by grounding the LLM’s answers in real document context.

---

## Key Features

- Upload documents for knowledge ingestion
- Semantic chunking using configurable chunk length
- Vector embeddings using a Sentence Transformer model
- Vector storage and similarity search with ChromaDB
- Retrieval-Augmented Generation for contextual responses
- FastAPI backend with REST endpoints
- Environment-based configuration using `.env`

---

## Technologies Used

- Python
- FastAPI
- ChromaDB
- Sentence Transformers
- Google Gemini LLM
- HuggingFace embeddings

Core tools used in this implementation include:

- :contentReference[oaicite:0]{index=0}  
- :contentReference[oaicite:1]{index=1}  
- :contentReference[oaicite:2]{index=2}  
- :contentReference[oaicite:3]{index=3}  

---

---

## Project Structure

semantic-chunking-rag-system/

main.py
chroma_db.py
requirements.txt
README.md
.env.example

data/
utils/


- **main.py** – FastAPI application and endpoints  
- **chroma_db.py** – Vector database integration  
- **data/** – Uploaded documents storage  
- **requirements.txt** – Project dependencies  
- **.env.example** – Example environment variables configuration  


## Environment Configuration

The project uses environment variables for configuration.

Create a `.env` file in the project root based on `.env.example`.

Example:
HF_API_KEY=your_huggingface_key
EMBED_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
GEMINI_API_KEY=your_gemini_api_key
LLM_MODEL_NAME=gemini-2.5-flash
CHROMA_DB_HOST=localhost
RAG_DATA_DIR=data
CHUNK_LENGTH=500
PORT=8000


## Installation

Clone the repository:
git clone https://github.com/yourusername/semantic-chunking-rag-system.git


Navigate into the project directory:
cd semantic-chunking-rag-system


Install dependencies:
pip install -r requirements.txt



## Running the Application

Start the FastAPI server:

uvicorn main:app --reload


The application will start on:
http://localhost:8000


Interactive API documentation is available at:
http://localhost:8000/docs



## API Endpoints

### 1. Health Check

**Endpoint**

---

## API Endpoints

### 1. Health Check

**Endpoint**
GET /health


**Description**

Checks if the application is running.

---

### 2. Upload Documents

**Endpoint**

**Description**

Checks if the application is running.

---

### 2. Upload Documents

**Endpoint**

**Description**

Checks if the application is running.

---

### 2. Upload Documents

**Endpoint**

**Description**

Checks if the application is running.

---

### 2. Upload Documents

**Endpoint**
POST /upload

**Content Type**
multipart/form-data

**Field**
files


This endpoint uploads documents which are processed, chunked, and stored in the vector database.

---

### 3. Chat with Documents

**Endpoint**
POST /chat

**Content Type**
application/json

Example request:
{
"query": "Explain the concept of tokenization in NLP"
}


The system retrieves the most relevant document chunks and sends them to the LLM to generate a context-aware response.

---

## Example Workflow

1. Start the API server.
2. Upload a PDF document using `/upload`.
3. Send a query to `/chat`.
4. The system retrieves relevant chunks and generates an answer using the LLM.

---

## Dependencies

All project dependencies are listed in:
requirements.txt


Key libraries include:

- FastAPI
- Uvicorn
- ChromaDB
- Sentence Transformers
- Google Generative AI
- Python Dotenv

---

## Author

Aniebiet Inyang

AI for Developers Track – KodeCamp 6.0

---

## License

This project is for educational purposes as part of the KodeCamp AI for Developers program.
=======
# semantic-chunking-rag-system
This project implements a RAG system that allows users to upload documents and ask questions about them using NLP. The system processes uploaded documents by performing semantic chunking, generating vector embeddings, storing them in a vector database, and retrieving relevant information to answer user queries using a large language model.
>>>>>>> 5eb8809854e895e53a65667d4285859be0a5caff
