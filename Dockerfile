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

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

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
