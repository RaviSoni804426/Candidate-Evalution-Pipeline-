# Build frontend
FROM node:18 AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --legacy-peer-deps
COPY frontend/ .
RUN npm run build

# Runtime image
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# System deps (add as-needed for native packages)
RUN apt-get update && apt-get install -y \
    build-essential \
    ca-certificates \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Copy and install python deps
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend code and frontend build
COPY backend ./backend
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

# Expose Hugging Face standard port
ENV PORT=7860
EXPOSE 7860

# Run the FastAPI app; ensure it listens on $PORT
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7860} --app-dir backend"]
