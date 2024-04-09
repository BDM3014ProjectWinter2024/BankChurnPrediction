# Use the official Python image as the base image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the inference script into the container
COPY inference.py /app/inference.py

# Copy the trained model file into the container
COPY random_forest.pkl /app/random_forest.pkl

# Set the entry point to the inference script
ENTRYPOINT ["python", "inference.py"]