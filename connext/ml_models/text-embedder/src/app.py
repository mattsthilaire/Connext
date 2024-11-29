import logging

import runpod
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)
logging.basicConfig(filename="example.log", encoding='utf-8', level=logging.INFO)


# Load model
logging.info("Loading model")
model = SentenceTransformer("all-MiniLM-L6-v2")
logging.info("Model loaded Successfully")

def handler(event):
    try:
        # Get the image data from the event
        logging.info("Getting image data")
        text = event["input"]["text"]
        embedding = model.encode(text).tolist()

        return {"embedding": embedding}
    except Exception as e:
        return {"error": str(e)}

runpod.serverless.start({"handler": handler})