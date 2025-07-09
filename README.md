# AIMeetupMind

Smart transcript processor for AI meetups — extracts speaker summaries, builds vector search with FAISS, and answers questions using RAG
Features

    Generates summaries containing the main ideas presented in the meetup by speaker
    Stores data in SQLite and JSON
    Creates vector embeddings with SentenceTransformers
    Builds FAISS index for fast semantic search
    Uses local free to use LLMs
    Ask questions like: “What did Mihai say about alignment?” or “What’s Ioana’s view on AI agents?”

    Python + Tkinter (GUI)
    FAISS (vector search)
    SentenceTransformers (all-MiniLM-L6-v2)
    Mistral or OpenAI GPT for answering
    SQLite, JSON for data storage

 Usage

    Run the GUI app
    Add a transcript
    Process it → chunks + embeddings are created
    Ask questions using natural language
