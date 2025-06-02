# Use the official Apify Python base image
FROM apify/actor-python:3.11

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install yt-dlp and ffmpeg for video processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy source code
COPY . ./

# Set the default command to run the Actor
CMD ["python", "main.py"]
