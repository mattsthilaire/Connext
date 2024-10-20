import string
from typing import List

def preprocess(text: str) -> str:
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    
    return text

def tokenize(text: str) -> List:
    preprocessed_text = preprocess(text)
    tokens = preprocessed_text.split()
    tokens = [token.strip() for token in tokens if token]
    return tokens