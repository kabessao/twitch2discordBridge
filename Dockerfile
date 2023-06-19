# Use an official Python runtime as the base image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the configuration file to the container
COPY config.yaml .

# Copy the Python script to the container
COPY bot.py .

# Set the entry point for the container
CMD ["python", "bot.py"]
