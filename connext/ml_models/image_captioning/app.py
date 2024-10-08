import json
import base64
from PIL import Image
import io
from transformers import BlipProcessor, BlipForConditionalGeneration

# Load model during cold start
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

def handler(event, context):
    # Decode the image
    image_data = base64.b64decode(event['body'])
    image = Image.open(io.BytesIO(image_data))

    # Generate caption
    inputs = processor(image, return_tensors="pt")
    out = model.generate(**inputs)
    caption = processor.decode(out[0], skip_special_tokens=True)

    return {
        'statusCode': 200,
        'body': json.dumps({'caption': caption})
    }