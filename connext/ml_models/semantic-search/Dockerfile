FROM --platform=linux/amd64 public.ecr.aws/lambda/python:3.11

# Install system dependencies if needed
RUN yum update -y && yum install -y \
    gcc \
    gcc-c++ \
    && yum clean all

# Copy requirements file
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy function code
COPY semantic-search/ ${LAMBDA_TASK_ROOT}/

# Set the CMD to your handler
CMD [ "app.lambda_handler" ]