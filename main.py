from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
import uuid
from io import BytesIO
import dotenv
import chromadb
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

# Load environment variables
dotenv.load_dotenv()

# -------------------- Configuration --------------------
HF_API_KEY = os.environ.get("HF_API_KEY")
EMBED_MODEL_NAME = os.environ.get("EMBED_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
CHROMA_DB_HOST = os.environ.get("CHROMA_DB_HOST", "localhost")
CHROMA_DB_PORT = os.environ.get("CHROMA_DB_PORT", "8000")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
LLM_MODEL_NAME = os.environ.get("LLM_MODEL_NAME", "gemini-2.5-flash")
DATA_DIR = os.environ.get("RAG_DATA_DIR", "./data")
CHUNK_LENGTH = int(os.environ.get("CHUNK_LENGTH", 500))
SERVER_PORT = int(os.environ.get("SERVER_PORT", 8000))

# Create the data directory
os.makedirs(DATA_DIR, exist_ok=True)

# -------------------- Model & DB Initialization --------------------
# Initialize Embedding Model
embed_model = SentenceTransformer(EMBED_MODEL_NAME)

# Initialize ChromaDB (Using HTTP Client to respect host/port requirements)
try:
    chroma_client = chromadb.HttpClient(host=CHROMA_DB_HOST, port=int(CHROMA_DB_PORT))
except Exception:
    # Fallback to ephemeral/persistent client if server connection isn't running locally
    chroma_client = chromadb.PersistentClient(path=os.path.join(DATA_DIR, "chroma"))

collection = chroma_client.get_or_create_collection(name="rag_collection")

# Initialize Gemini LLM
genai.configure(api_key=GEMINI_API_KEY)
llm_model = genai.GenerativeModel(LLM_MODEL_NAME)

# -------------------- FastAPI App Setup --------------------
app = FastAPI(title="Semantic-chunking RAG API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# File parsing safety
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import docx
except ImportError:
    docx = None

# -------------------- Helper Functions --------------------
def semantic_chunk_text(text: str, max_chunk_len: int = CHUNK_LENGTH) -> List[str]:
    """Splits text semi-semantically by groups of sentences up to CHUNK_LENGTH."""
    # Split sentences roughly by common punctuations
    sentences = text.replace('\n', ' ').split('. ')
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        if len(current_chunk) + len(sentence) <= max_chunk_len:
            current_chunk += (sentence + ". ")
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
            
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def extract_text(filename: str, content: bytes) -> str:
    lower = filename.lower()
    if lower.endswith(".txt") or lower.endswith(".md"):
        try:
            return content.decode("utf-8")
        except Exception:
            return content.decode("latin-1", errors="ignore")

    if lower.endswith(".pdf"):
        if PyPDF2 is None:
            raise HTTPException(500, "PyPDF2 library not installed")
        reader = PyPDF2.PdfReader(BytesIO(content))
        return "\n".join([p.extract_text() or "" for p in reader.pages])

    if lower.endswith(".docx"):
        if docx is None:
            raise HTTPException(500, "python-docx library not installed")
        d = docx.Document(BytesIO(content))
        return "\n".join([p.text for p in d.paragraphs])

    return content.decode("utf-8", errors="ignore")

# Pydantic Model for JSON Prompt payload
class PromptPayload(BaseModel):
    query: str

# -------------------- Endpoint Requirements --------------------

@app.post("/upload")
def upload_files(files: UploadFile = File(...)):
    """Accepts single or multi-part document, chunks it semantically, and stores it."""
    try:
        content = files.file.read()
        text = extract_text(files.filename, content)
        
        # Perform explicit semantic chunking
        chunks = semantic_chunk_text(text, CHUNK_LENGTH)
        
        if not chunks:
            return {"message": "No text content found to split."}

        # Embed and prepare records for ChromaDB
        documents = []
        embeddings = []
        ids = []
        metadatas = []

        for chunk in chunks:
            vec = embed_model.encode(chunk).tolist()
            cid = str(uuid.uuid4())
            
            documents.append(chunk)
            embeddings.append(vec)
            ids.append(cid)
            metadatas.append({"filename": files.filename})

        # Save to Chroma
        collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )

        return {"filename": files.filename, "chunks_created": len(chunks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/prompt")
def prompt(payload: PromptPayload):
    """Retrieves document context from ChromaDB and builds a response using Gemini."""
    try:
        query_text = payload.query
        query_vec = embed_model.encode(query_text).tolist()

        # Retrieve top 3 relevant chunks
        results = collection.query(
            query_embeddings=[query_vec],
            n_results=3
        )

        retrieved_docs = results.get("documents", [[]])[0]
        if not retrieved_docs:
            return {"answer": "I cannot find the answer in the provided document."}

        context_block = "\n\n".join(retrieved_docs)
        
        prompt_instruction = f"""
You are an AI assistant answering questions based only on the provided document context.

Instructions:
- Use ONLY the information in the context below.
- If the answer is not present in the context, say: "I cannot find the answer in the provided document."
- Be clear and concise.

Context:
{context_block}

Question:
{query_text}

Answer:
"""
        response = llm_model.generate_content(prompt_instruction)

        return {
            "answer": response.text,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health", status_code=status.HTTP_200_OK)
def health():
    """Simple endpoint to return a 200 to indicate that the app is live."""
    return {"status": "live"}
