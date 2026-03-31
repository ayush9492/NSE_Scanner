# Use Python 3.11 slim as base
FROM python:3.11-slim

# Install system dependencies + TA-Lib C library
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    wget \
    && wget -q http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz \
    && tar -xzf ta-lib-0.4.0-src.tar.gz \
    && cd ta-lib \
    && ./configure --prefix=/usr \
    && make \
    && make install \
    && cd .. \
    && rm -rf ta-lib ta-lib-0.4.0-src.tar.gz \
    && apt-get purge -y build-essential wget \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY index.html .

# Railway sets PORT env variable
ENV PORT=8000
EXPOSE 8000

CMD uvicorn app:app --host 0.0.0.0 --port $PORT