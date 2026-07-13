FROM python:3.11-slim
WORKDIR /app
# Build context is the REPO ROOT (not backend/), because backend/main.py
# uses package-qualified imports (`from backend.routers import ...`) — the
# image needs an /app/backend/ package directory, not a flattened /app/.
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./backend/
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
