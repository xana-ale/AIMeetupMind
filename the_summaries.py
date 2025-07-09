from sentence_transformers import SentenceTransformer
import ollama
import re




def clean_transcript(text):

    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def generate_summary(transcript):

    """ Transcript to summary """    

    cleaned_transcript = clean_transcript(transcript)

    prompt = f"""
    You are an AI assistant that reads the transcript of an AI meetup.
    Your task is to extract the most important ideas presented by each speaker.
    
    For each speaker, list clearly:
    - The main topic they presented.
    - The key problems or challenges discussed.
    - The proposed solutions or suggestions.
    - Any relevant examples if present.
    
    Be concise but comprehensive. Don't include chit-chat or introductions.
    
    Transcript:
    {cleaned_transcript}
    
    Summary:
    """

    response = ollama.chat(
        model="mistral",
        messages=[
            {"role": "user", "content": prompt}  # system
        ]
    )

    result = response['message']['content']
    return result
