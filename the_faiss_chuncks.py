# -*- coding: utf-8 -*-
"""
Created on Wed Jul  2 14:17:24 2025

@author: alex
"""

import re


def chunk_by_speaker(transcript, max_tokens=300):
    """
    Split transcript by speaker turns, then optionally by length.
    """
    # Split based on speaker tags like "Adrian:", "Speaker 1:", etc.
    speaker_blocks = re.split(r'(\w+:)', transcript)

    chunks = []
    current_speaker = ""
    current_text = ""

    for part in speaker_blocks:
        if re.match(r'\w+:', part):
            # If there is already some text, process it
            if current_text:
                # Further split into token-based chunks if needed
                sub_chunks = split_long_text(current_speaker + " " + current_text, max_tokens)
                chunks.extend(sub_chunks)
                current_text = ""
            current_speaker = part.strip()
        else:
            current_text += " " + part.strip()

    # Don't forget the last chunk
    if current_text:
        sub_chunks = split_long_text(current_speaker + " " + current_text, max_tokens)
        chunks.extend(sub_chunks)

    return chunks


def split_long_text(text, max_tokens):
    """
    Further split long text into smaller chunks based on max_tokens.
    """
    words = text.split()
    if len(words) <= max_tokens:
        return [text]

    sub_chunks = []
    for i in range(0, len(words), max_tokens):
        sub_chunk = " ".join(words[i:i + max_tokens])
        sub_chunks.append(sub_chunk)

    return sub_chunks
