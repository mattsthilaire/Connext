import json
import boto3
import joblib
from pathlib import Path
import os

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

s3 = boto3.client("s3")

LOCAL_PATH = Path("/tmp")
EMBDEDDING = None
VECTORIZER = None


def download_tfidf_files():
    bucket = os.environ["BUCKET"]

    embedding_matrix_key = os.environ["EMBEDDING_KEY"]
    vectorizer_key = os.environ["VECTORIZER_KEY"]

    s3.download_file(bucket, embedding_matrix_key, LOCAL_PATH / "tfidf_embedding.joblib")
    s3.download_file(bucket, vectorizer_key, LOCAL_PATH / "tfidf_vectorizer.joblib")

def load_models():

    global EMBEDDING, VECTORIZER
    EMBEDDING = joblib.load(LOCAL_PATH / "tfidf_embedding.joblib")
    VECTORIZER = joblib.load(LOCAL_PATH / "tfidf_vectorizer.joblib")

def similarity_search(query: str, topk: int = 5):
    """
    Computes cosine similarity scores for Tfidf vectors. The embedding and TfidfVectorizer are pretrained from previous
    data. Updated will need a retraining scheme.

    Inputs:
        - embedding (scipy sparse matrix): matrix of all docuement or description embeddings
        - vectorizer (pretrianed tfidf vectorizer): TfidfVectorizer pretrain on all descriptions
        - query (str): query string to compare other documents to
        - topk (int): Number of results to give

    Outputs:
        - topk scores returned as indices. Indices are mapped to a photos ID for now. Will have to amend in the future. 
    """

    global EMBEDDING, VECTORIZER

    query_vector = VECTORIZER.transform([query])
    scores = cosine_similarity(EMBEDDING, query_vector)
    topk_scores = np.argsort(scores, axis=0)[-topk:][::-1]

    return topk_scores.flatten().tolist()

download_tfidf_files()
load_models()

def lambda_handler(event, context):

    try:
        body = json.loads(event.get("body", "{}"))
        query = body["query"]
        topk = body.get("topk", 5)
        
        top_ids = similarity_search(query, topk)

        return {
            "statusCode": 200,
            "body": json.dumps({"top_ids": top_ids})
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"}),
            "headers": {
                "Content-Type": "application/json"
            }
        }

if __name__ == "__main__":

    event = {
        "query": "my_test_string",
        "topk": 5
    }
    
    lambda_handler(event, None)