import re

def strip_newlines(s: str):
    return re.sub(r'\n\s*', '', s)