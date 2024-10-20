import os
os.environ['HF_HOME'] = '/model'

from transformers import BlipProcessor, BlipForConditionalGeneration;
processor = BlipProcessor.from_pretrained('Salesforce/blip-image-captioning-base')
model = BlipForConditionalGeneration.from_pretrained('Salesforce/blip-image-captioning-base')

processor.save_pretrained("./model/processor")
model.save_pretrained("./model/model")