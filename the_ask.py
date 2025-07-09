# -*- coding: utf-8 -*-

from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json
import ollama


# Load the same embedding model
embedder = SentenceTransformer('all-MiniLM-L6-v2')


def load_faiss_index(index_path):
    return faiss.read_index(index_path)


def load_metadata(metadata_path):
    with open(metadata_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def embed_query(query):
    embedding = embedder.encode([query])
    return np.array(embedding).astype('float32')


def search_index(query_embedding, index, metadata, top_k=6):
    D, I = index.search(query_embedding, top_k)
    results = []
    for idx in I[0]:
        if idx < len(metadata):
            results.append(metadata[idx])
    return results


def build_prompt(query, retrieved_chunks):
    context = "\n\n".join([f"{chunk['speaker']}: {chunk['text']}" for chunk in retrieved_chunks])
    prompt = f"""
You are an assistant for AI Meetup Summaries.

Here is the context from the meetup:

{context}

Answer the following question based on the context above:
{query}

If the context does not contain the answer, say 'The context does not contain this information.'
"""
    return prompt


def ask_question(query, index_path, metadata_path, model='mistral'):
    # Load FAISS index and metadata
    index = load_faiss_index(index_path)
    metadata = load_metadata(metadata_path)

    # Embed the query
    query_embedding = embed_query(query)

    # Search
    results = search_index(query_embedding, index, metadata)
    
    
    
    # Build the prompt
    prompt = build_prompt(query, results)

    # Call Ollama
    response = ollama.chat(model=model, messages=[
        {'role': 'user', 'content': prompt}
    ])

    return response['message']['content']
