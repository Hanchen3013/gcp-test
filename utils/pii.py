import re

def mask_pii(text: str) -> str:
    return re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "[SSN]", text)
