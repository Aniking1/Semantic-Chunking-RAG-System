import chromadb
from sentence_transformers import SentenceTransformer
import uuid

client = chromadb.Client()

collection = client.get_or_create_collection(name="rag_docs")

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def store_chunks(texts, metadatas=None):

    embeddings = model.encode(texts).tolist()

    ids = [str(uuid.uuid4()) for _ in texts]

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas
    )


def query_chunks(query, k=5):

    q_embedding = model.encode([query]).tolist()

    results = collection.query(
        query_embeddings=q_embedding,
        n_results=k
    )

    return results["documents"][0]

