# Use an official Python runtime as the base image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# ARG statement to declare the build argument
ARG CONFIG=config

# Copy the Python script to the container
COPY *.py .

# Copy the configuration file to the container
COPY ${CONFIG}.yaml ./config.yaml

# Set the entry point for the container
CMD ["python", "bot.py"]
