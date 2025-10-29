# Multi-stage build for Video Editor Prototype
# Stage 1: Build Frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Setup Python Backend
FROM python:3.11-slim

# Install system dependencies (excluding ffmpeg - will install 8.0 manually)
RUN apt-get update && apt-get install -y \
    wget \
    xz-utils \
    libmagic1 \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# Install FFmpeg 8.0 static binary (same version as local macOS)
# Source: John Van Sickle's FFmpeg builds (official, trusted source)
RUN wget -q https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz \
    && tar -xf ffmpeg-release-amd64-static.tar.xz \
    && mv ffmpeg-*-amd64-static/ffmpeg /usr/local/bin/ \
    && mv ffmpeg-*-amd64-static/ffprobe /usr/local/bin/ \
    && rm -rf ffmpeg-*-amd64-static* \
    && chmod +x /usr/local/bin/ffmpeg /usr/local/bin/ffprobe \
    && ffmpeg -version

WORKDIR /app

# Copy backend requirements and install Python dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt
RUN pip install --no-cache-dir gunicorn==21.2.0

# Copy backend code
COPY backend/ ./backend/

# Copy built frontend from stage 1
COPY --from=frontend-builder /app/frontend/dist ./backend/static/

# Create necessary directories
RUN mkdir -p /app/backend/database

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=5001

WORKDIR /app/backend

# Expose port
EXPOSE $PORT

# Start gunicorn
CMD gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --log-level info
