FROM python:3.11-slim

WORKDIR /app

# Install TA-Lib C library
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential wget && \
    rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY backend/app.py .
COPY frontend/index.html ./static/index.html

# Serve frontend from FastAPI
RUN echo '\n\
from fastapi.staticfiles import StaticFiles\n\
from fastapi.responses import FileResponse\n\
import os\n\
\n\
# Mount after app is created in app.py\n\
' >> /tmp/mount_note.txt

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]