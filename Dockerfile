# Use the official Python image from the Docker Hub
FROM python:3.10

# Install Git
RUN apt-get update && apt-get install -y git

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the working directory contents into the container at /app
COPY . .

# Run uvicorn app when the container launches
CMD ["python", "app.py"]
