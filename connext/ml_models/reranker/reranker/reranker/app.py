import json
import os
from typing import List

def lambda_handler(event, context):

    try:
        K = 60
        body = json.loads(event.get("body", "{}"))
        rankers = body["rankers"]
        topk = body.get("topk", 5)
        
        ranked_idx = {}
        for ranker in rankers:
            for i,rank in enumerate(rankers[ranker]):
                ranked_idx[rank] = ranked_idx.get(rank, 0) + (1 / (K + (i+1)))

        sorted_ranks = sorted(ranked_idx.items(), key=lambda x: x[1])
        ranked_idx = [idx for idx, _ in sorted_ranks][-topk:][::-1]

        return {
            "statusCode": 200,
            "body": json.dumps({"ranked_idx": ranked_idx})
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