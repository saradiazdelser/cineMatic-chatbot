# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy current directory contents into the container at /app
COPY . /app

# Command to run the application
CMD ["python", "app.py", "--host", "0.0.0.0", "--port", "6000"]
