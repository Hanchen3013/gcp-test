import re

def clean_transcript(text: str) -> str:
    text = re.sub(r"\b(um+|uh+|like|you know)\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text)
    return text.strip()
