FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for markitdown and python-magic
RUN apt-get update && apt-get install -y \
    libmagic1 \
    libmagic-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all Python modules
COPY *.py ./
COPY __init__.py ./

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]