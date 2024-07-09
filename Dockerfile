# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the working directory contents into the container at /app
COPY . .

# Make port 8000 available
EXPOSE 8000


# Run app.py when the container launches
CMD ["uvicorn", "src.api:app", "--log-config=src/logging.yaml"]
