# Use the slim variant of Python 3.10
FROM python:3.10

# Set the working directory
WORKDIR /app

# Install required system packages
RUN apt-get update && \
    apt-get install -y python3-venv && \
    apt-get clean

# Copy the current directory contents into the container at /app
COPY . /app

# Create a virtual environment
RUN python3 -m venv venv

# Activate virtual environment and install dependencies
RUN /bin/bash -c "source /app/venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt"

# Run the application
CMD ["./venv/bin/python", "main.py"]
