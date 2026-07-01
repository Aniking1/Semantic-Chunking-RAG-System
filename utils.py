import os

def semantic_chunk_text(text: str, chunk_length: int):
    """
    Splits text into chunks based on a configurable chunk length.
    """

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_length
        chunk = text[start:end]
        chunks.append(chunk)
        start = end

    return chunks