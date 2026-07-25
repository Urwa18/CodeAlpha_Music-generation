# Base Python Image
FROM python:3.11-slim

# Set Working Directory
WORKDIR /app

# Install System Dependencies for Audio Synthesis
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    fluidsynth \
    fluid-soundfont-gm \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy Package Requirements
COPY requirements.txt .

# Install Python Dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy Project Files
COPY . .

# Expose Server Port
EXPOSE 8000

# Set Environment Variables
ENV PORT=8000
ENV HOST=0.0.0.0
ENV TF_CPP_MIN_LOG_LEVEL=2

# Container Entrypoint
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
