# Use the official Ubuntu image as the base image
FROM ubuntu:24.04

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive



# Install required packages and the snap7 library
RUN apt update \
    && apt install -y software-properties-common python3 python3-pip python3-venv \
    && apt update 

# Set the working directory
WORKDIR /app


# Create a virtual environment and install Python packages
RUN python3 -m venv /app/myenv

# Copy the requirements file and install the dependencies
COPY requirements.txt .
RUN /bin/bash -c "source /app/myenv/bin/activate && pip install --no-cache-dir -r requirements.txt"

# Copy the rest of the application code
COPY . .

# Set the entry point to run the Python script
ENTRYPOINT ["/bin/bash", "-c", "source /app/myenv/bin/activate && python3 main.py"]