# Stage 1: Build frontend
FROM node:22-alpine AS frontend-build
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# Stage 2: Python runtime
FROM python:3.12-slim AS runtime
WORKDIR /app

# Install backend dependencies
COPY backend/pyproject.toml .
RUN pip install --no-cache-dir .

# Copy backend source
COPY backend/ .

# Copy built frontend
COPY --from=frontend-build /app/dist /app/static

# Create data directory
RUN mkdir -p /app/data

ENV DOCFORGE_DATA_DIR=/app/data
ENV DOCFORGE_DB_PATH=/app/data/docforge.db
ENV DOCFORGE_UPLOAD_DIR=/app/data/uploads
ENV DOCFORGE_OUTPUT_DIR=/app/data/outputs

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
