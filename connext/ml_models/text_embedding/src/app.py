import json
import joblib
import os

import boto3
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

s3 = boto3.client("s3")

def download_tfidf(bucket, key, local_path):
    s3.download_file(bucket, key, local_path)
    
def download_embedding(bucket, key, local_path):
    s3.download_file(bucket, key, local_path)
    
def load_tfidf(local_path) -> TfidfVectorizer:
    return joblib.load(local_path)

def load_embedding(local_path: str) -> np.array:
    return joblib.load(local_path)

def calculate_similarities(embedding: np.array, query_vector: np.array, top_k: int = 100) -> np.array:
    similarities = cosine_similarity(query_vector, embedding)
    similar_indices = np.argsort(similarities)[-top_k:]
    return similar_indices.tolist()

def lambda_handler(event, context):
    bucket = os.environ["BUCKET"]
    key = os.environ["KEY"]
    query = event["query"]
    top_k = event["top_k"]
    
    local_path = "/tmp/tfidf_vectorizer.joblib"
    
    download_tfidf(bucket, key, local_path)
    vectorizer = load_tfidf(local_path)
    
    download_embedding(bucket, key, local_path)
    embedding = load_embedding(local_path)
    
    query_vector = vectorizer.transform([query])
    
    similar_indices = calculate_similarities(embedding, query_vector, top_k)
    
    return {
        "similar_indices": similar_indices,
    }