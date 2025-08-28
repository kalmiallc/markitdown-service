# MarkItDown Document Converter Service

A FastAPI service that converts various document formats to Markdown using Microsoft's MarkItDown library. The service can be deployed both as a Docker container and on AWS Lambda.

## Features

- Convert documents from URLs to Markdown format
- Support for multiple file formats: PDF, Word, PowerPoint, Excel, Images, HTML, and more
- RESTful API with OpenAPI/Swagger documentation
- Docker containerization support
- AWS Lambda deployment ready
- File size validation (50MB limit) with memory monitoring
- Comprehensive error handling and logging
- CORS enabled for web applications
- Async HTTP client with connection pooling for better performance
- File type validation using magic bytes
- Conversion timeout protection (120s)
- Real-time memory usage monitoring
- Processing time tracking

## Supported File Formats

- **Documents**: PDF, DOCX, PPTX, XLSX
- **Images**: JPG, JPEG, PNG, GIF (with OCR)
- **Web**: HTML
- **Text**: TXT, CSV, JSON, XML
- **Archives**: ZIP, EPUB

## Project Structure

```
├── __init__.py          # Python package initialization
├── main.py              # FastAPI application and endpoints
├── config.py            # Configuration constants and settings
├── security.py          # SSRF protection and URL validation
├── models.py            # Pydantic models for request/response
├── utils.py             # Utility functions (memory, file validation)
├── conversion.py        # Document conversion with MarkItDown
├── requirements.txt     # Python dependencies
├── lambda_requirements.txt # Lambda-specific dependencies
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker Compose setup
├── serverless.yml      # Serverless Framework config
├── deploy.sh           # AWS Lambda deployment script
├── test_ssrf_protection.py # SSRF protection test suite
└── README.md           # This file
```

## Quick Start

### Option 1: Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build and run manually
docker build -t markitdown-service .
docker run -p 8000:8000 markitdown-service
```

### Option 2: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
python main.py
```

The service will be available at `http://localhost:8000`

### Option 3: AWS Lambda

```bash
# Install Serverless Framework
npm install -g serverless
npm install serverless-python-requirements

# Deploy to AWS
./deploy.sh
```

## API Usage

### Health Check
```bash
GET /health
```

### Convert Document
```bash
POST /convert
Content-Type: application/json

{
  "url": "https://example.com/document.pdf"
}
```

**Response:**
```json
{
  "success": true,
  "markdown": "# Document Title\n\nContent...",
  "file_type": ".pdf",
  "error": "",
  "processing_time": 2.34,
  "file_size": 1048576
}
```

### Example with cURL
```bash
curl -X POST "http://localhost:8000/convert" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com/sample.pdf"}'
```

## API Documentation

Once the service is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Configuration

### Environment Variables
- `PYTHONPATH`: Python path for Lambda deployment
- `PYTHONUNBUFFERED`: Disable Python output buffering

### Limitations
- Maximum file size: 50MB
- Download timeout: 30 seconds
- Conversion timeout: 120 seconds
- Memory increase limit: 500MB
- Supported URL schemes: HTTP/HTTPS only

## Development

### Module Organization

The codebase is organized into logical modules:

- **`main.py`**: FastAPI application, endpoints, and HTTP client management
- **`config.py`**: All configuration constants and settings
- **`security.py`**: SSRF protection and URL validation logic
- **`models.py`**: Pydantic models for request/response validation
- **`utils.py`**: Utility functions for file handling and memory monitoring
- **`conversion.py`**: Document conversion logic using MarkItDown

### Adding New Features
1. Update relevant modules based on functionality
2. Update `requirements.txt` if adding dependencies
3. Test locally with `python main.py`
4. Run SSRF tests with `python test_ssrf_protection.py`
5. Build and test with Docker
6. Deploy to Lambda if needed

## Error Handling

The service includes comprehensive error handling for:
- URL security validation failures
- Invalid URLs or unsupported schemes
- Network timeouts and connection errors
- File size limits exceeded
- Memory usage limits exceeded
- Unsupported file formats
- Conversion failures and timeouts
- Temporary file cleanup errors

All errors are logged and returned in a structured format.

## Security Considerations

- **SSRF Protection**: Comprehensive validation blocks access to private networks, localhost, and cloud metadata endpoints
- **File size limits** prevent resource exhaustion attacks (50MB limit)
- **Memory monitoring** prevents memory exhaustion during processing
- **URL validation** ensures only HTTP/HTTPS schemes and safe ports (80, 443, 8080, 8443)
- **File type validation** using magic bytes prevents malicious file processing
- **Temporary file cleanup** prevents disk space exhaustion
- **Conversion timeouts** prevent DoS through long-running processes
- **User-Agent header** added to all outbound requests
- **CORS configured** for web application integration

### Blocked Resources (SSRF Protection)
- Private networks: 127.0.0.0/8, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16
- Link-local addresses: 169.254.0.0/16
- Localhost variations: localhost, 127.0.0.1, 0.0.0.0, ::1
- Cloud metadata endpoints: 169.254.169.254, metadata.google.internal, metadata.azure.com
- Suspicious hostname patterns containing 'metadata' or 'internal'
- Dangerous ports (only 80, 443, 8080, 8443 allowed)

## Testing

### SSRF Protection Tests
```bash
python test_ssrf_protection.py
```

This runs a comprehensive test suite covering 30 different SSRF attack vectors to ensure the security validation is working correctly.

## License

This service uses Microsoft's MarkItDown library. Please refer to the original library's license terms.