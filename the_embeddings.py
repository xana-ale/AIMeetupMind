import os
import json
import re
import faiss
import numpy as np
from typing import List, Dict
from sentence_transformers import SentenceTransformer

DB_PATH = 'C:/Users/alex/New folder/meetmind/'
INDEX_PATH = os.path.join(DB_PATH, 'faiss_index_meetupmind.index')
METADATA_PATH = os.path.join(DB_PATH, 'metadata_meetupmind.json')
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'




os.makedirs(DB_PATH, exist_ok=True)
if not os.path.exists(METADATA_PATH):
    with open(METADATA_PATH, 'w', encoding='utf-8') as f:
        json.dump([], f)

embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)



def split_by_speaker(transcript):
    """
    Splits transcript into chunks based on 'Speaker N (Name):' format.
    """
    pattern = r'Speaker\s+\d+\s+\([^)]+\):'
    matches = list(re.finditer(pattern, transcript))

    chunks = []
    for i in range(len(matches)):
        start = matches[i].end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(transcript)
        speaker_line = matches[i].group()
        speaker = speaker_line.replace("Speaker", "").split("(", 1)[-1].rstrip("):").strip()
        text = transcript[start:end].strip()
        if text:
            chunks.append({'speaker': speaker, 'text': text})
    return chunks


def embed_chunks(chunks: List[Dict[str, str]]) -> np.ndarray:
    """
    Generates embeddings for a list of text chunks.
    """
    texts = [chunk['text'] for chunk in chunks]
    embeddings = embedder.encode(texts)
    return np.array(embeddings, dtype='float32')


def load_or_create_faiss_index(index_path: str, dim: int) -> faiss.Index:
    """
    Loads an existing FAISS index or creates a new one with the given dimension.
    """
    if os.path.exists(index_path):
        try:
            return faiss.read_index(index_path)
        except Exception as e:
            raise RuntimeError(f"Failed to load FAISS index at {index_path}: {e}")
    else:
        return faiss.IndexFlatL2(dim)


def load_metadata(metadata_path: str) -> List[Dict]:
    """
    Loads the metadata file or returns an empty list if it doesn't exist.
    """
    try:
        with open(metadata_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Couldn't load metadata from {metadata_path}. Starting fresh. Reason: {e}")
        return []


def save_metadata(metadata: List[Dict], metadata_path: str) -> None:
    """
    Saves the metadata list to a JSON file.
    """
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=4)


# ==== Main Function ====

def process_and_store_transcript(date: str, meetup_name: str, transcript: str) -> None:
    """
    Processes the transcript: splits it, embeds, stores in FAISS, and updates metadata.
    """
    print(" Processing transcript...")

    # Split and check
    chunks = split_by_speaker(transcript)
    if not chunks:
        print(" No chunks extracted. Aborting.")
        return

    embeddings = embed_chunks(chunks)
    dim = embeddings.shape[1]

    index = load_or_create_faiss_index(INDEX_PATH, dim)
    start_id = index.ntotal

    index.add(embeddings)
    faiss.write_index(index, INDEX_PATH)

    # Load and update metadata
    metadata = load_metadata(METADATA_PATH)
    for i, chunk in enumerate(chunks):
        metadata.append({
            'id': start_id + i,
            'date': date,
            'meetup_name': meetup_name,
            'speaker': chunk['speaker'],
            'text': chunk['text']
        })
    save_metadata(metadata, METADATA_PATH)

    print(f" Done. {len(chunks)} chunks added to FAISS index.")
