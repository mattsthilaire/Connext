FROM public.ecr.aws/lambda/python:3.9

# Install dependencies
RUN pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu
RUN pip install transformers pillow

# Copy function code
COPY app.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler
CMD [ "app.handler" ]
