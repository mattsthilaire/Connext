import logging

import runpod
from PIL import Image
import base64
import io
from transformers import BlipProcessor, BlipForConditionalGeneration

logger = logging.getLogger(__name__)
logging.basicConfig(filename="example.log", encoding='utf-8', level=logging.INFO)


# Load model
logging.info("Loading model")
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
logging.info("Model loaded Successfully")

def handler(event):
    try:
        # Get the image data from the event
        logging.info("Getting image data")
        image_data = event["input"]["image"]
        image = Image.open(io.BytesIO(base64.b64decode(image_data)))

        # Generate caption
        logging.info("Generating caption")
        inputs = processor(image, return_tensors="pt")
        out = model.generate(**inputs)
        caption = processor.decode(out[0], skip_special_tokens=True)

        return {"caption": caption}
    except Exception as e:
        return {"error": str(e)}

runpod.serverless.start({"handler": handler})