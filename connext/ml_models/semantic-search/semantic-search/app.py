import json
import boto3
import logging
from pathlib import Path
import os
from typing import List

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")
LOCAL_PATH = Path("/tmp")
EMBDEDDING = None


def download_files():

    global EMBEDDING
    bucket = os.environ["BUCKET"]
    embedding_matrix_key = os.environ["EMBEDDING_KEY"]

    logger.info(f"Downloading embedding matrix from s3://{bucket}/{embedding_matrix_key}")
    s3.download_file(bucket, embedding_matrix_key, LOCAL_PATH / "semantic_embedding.npy")
    
    EMBEDDING = np.load(LOCAL_PATH / "semantic_embedding.npy")
    logger.info(f"Successfully loaded embedding matrix with shape: {EMBEDDING.shape}")

def similarity_search(query: List[float], topk: int = 5):
    """
    Computes cosine similarity scores for Tfidf vectors. The embedding and TfidfVectorizer are pretrained from previous
    data. Updated will need a retraining scheme.

    Inputs:
        - query (list): list of floats representing an embedding of a string
        - topk (int): Number of results to give

    Outputs:
        - topk scores returned as indices. Indices are mapped to a photos ID for now. Will have to amend in the future. 
    """

    global EMBEDDING

    logger.info(f"Computing similarity search for query of length {len(query)}, topk={topk}")
    scores = cosine_similarity(EMBEDDING, np.array(query).reshape(1, -1))
    topk_scores = np.argsort(scores, axis=0)[-topk:][::-1]
    logger.info("Similarity search completed.")

    return topk_scores.flatten().tolist()

download_files()

def lambda_handler(event, context):

    request_id = context.aws_request_id if context else "local-development"
    logger.info(f"Processing request {request_id}")

    try:
        body = json.loads(event.get("body", "{}"))
        query = body["query"]
        topk = body.get("topk", 5)
        logger.info(f"Query length: {len(query)}, requested top-k: {topk}")
        
        ordered_idx = similarity_search(query, topk)
        logger.info(f"Request completed successfully.")

        return {
            "statusCode": 200,
            "body": json.dumps({"ordered_ids": ordered_idx})
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
        "query": [0.2, 0.4, 0.7]
    }
    
    lambda_handler(event, None)