import re

def newlines_to_spaces(s: str):
    return re.sub(r'\n\s*', ' ', s).strip()