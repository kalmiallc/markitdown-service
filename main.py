import os
import tempfile
import asyncio
import time
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional
from urllib.parse import urlparse
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import httpx
import magic

# Add current directory to Python path for module imports
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Local imports
from config import (
    MAX_FILE_SIZE, MAX_MEMORY_INCREASE, CHUNK_SIZE,
    MAX_CONNECTIONS, MAX_KEEPALIVE_CONNECTIONS, HTTP_TIMEOUT, USER_AGENT,
    FILE_TYPE_MAPPING
)
from models import ConvertRequest, ConvertResponse
from security import validate_url_security
from utils import validate_file_type, get_memory_usage, get_file_extension_from_mime
from conversion import convert_with_timeout

logging.basicConfig(level=logging.INFO)

# Global HTTP client for connection pooling
http_client: Optional[httpx.AsyncClient] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    global http_client
    http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(HTTP_TIMEOUT),
        limits=httpx.Limits(max_keepalive_connections=MAX_KEEPALIVE_CONNECTIONS, max_connections=MAX_CONNECTIONS),
        headers={"User-Agent": USER_AGENT}
    )
    logging.info("HTTP client initialized")
    
    yield
    
    # Shutdown
    if http_client:
        await http_client.aclose()
        logging.info("HTTP client closed")

app = FastAPI(
    title="Document to Markdown Converter",
    description="Convert documents from URLs to Markdown using Microsoft's MarkItDown library",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "markitdown-converter"}

@app.post("/convert", response_model=ConvertResponse)
async def convert_document(request: ConvertRequest) -> ConvertResponse:
    logger = logging.getLogger(__name__)
    temp_path = None
    start_time = time.time()
    
    # Monitor initial memory usage
    initial_memory = get_memory_usage()
    logger.info(f"Initial memory usage: {initial_memory['rss_mb']:.2f}MB ({initial_memory['percent']:.1f}%)")
    
    try:
        global http_client
        if not http_client:
            raise Exception("HTTP client not initialized")
            
        url_str = str(request.url)
        parsed_url = urlparse(url_str)
        
        logger.info(f"Processing conversion for URL: {url_str}")
        
        # Additional runtime URL security check (defense in depth)
        is_secure, security_message = validate_url_security(url_str)
        if not is_secure:
            logger.warning(f"Runtime URL security check failed: {security_message}")
            return ConvertResponse(
                success=False,
                error=f"URL security validation failed: {security_message}",
                processing_time=time.time() - start_time
            )
        
        # Get file extension from URL for temp file naming
        file_ext = os.path.splitext(parsed_url.path)[1].lower()
        
        try:
            # Download file using async HTTP client with streaming
            async with http_client.stream('GET', url_str) as response:
                response.raise_for_status()
                
                # Check content length
                content_length = response.headers.get('Content-Length')
                if content_length and int(content_length) > MAX_FILE_SIZE:
                    raise ValueError(f"File too large (>{MAX_FILE_SIZE // (1024*1024)}MB)")
                
                # Create temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
                    temp_path = temp_file.name
                
                # Download with size and memory monitoring
                downloaded_size = 0
                file_content = bytearray()
                
                async for chunk in response.aiter_bytes(chunk_size=CHUNK_SIZE):
                    downloaded_size += len(chunk)
                    
                    # Size check
                    if downloaded_size > MAX_FILE_SIZE:
                        raise ValueError(f"File too large (>{MAX_FILE_SIZE // (1024*1024)}MB)")
                    
                    # Memory check
                    current_memory = get_memory_usage()
                    if current_memory['rss_mb'] > initial_memory['rss_mb'] + MAX_MEMORY_INCREASE:
                        logger.warning(f"High memory usage detected: {current_memory['rss_mb']:.2f}MB")
                        raise ValueError("Memory usage limit exceeded during download")
                    
                    file_content.extend(chunk)
                
                # Validate file type using magic bytes
                if file_content:
                    detected_mime = validate_file_type(bytes(file_content))
                    if detected_mime:
                        detected_ext = get_file_extension_from_mime(detected_mime)
                        logger.info(f"Detected file type: {detected_mime} -> {detected_ext}")
                        file_ext = detected_ext
                    else:
                        logger.warning(f"Unsupported file type detected. MIME: {magic.from_buffer(bytes(file_content), mime=True)}")
                        return ConvertResponse(
                            success=False,
                            error="Unsupported file type detected",
                            processing_time=time.time() - start_time,
                            file_size=downloaded_size
                        )
                
                # Write to temp file
                with open(temp_path, 'wb') as f:
                    f.write(file_content)
            
            logger.info(f"Downloaded file of size: {downloaded_size} bytes, type: {file_ext}")
            
            # Monitor memory before conversion
            pre_conversion_memory = get_memory_usage()
            logger.info(f"Pre-conversion memory: {pre_conversion_memory['rss_mb']:.2f}MB")
            
            # Convert to markdown with timeout
            markdown_content = await convert_with_timeout(temp_path)
            
            if not markdown_content.strip():
                logger.warning("Conversion resulted in empty content")
                return ConvertResponse(
                    success=False,
                    error="Conversion resulted in empty content. The file may not be supported or may be corrupted.",
                    processing_time=time.time() - start_time,
                    file_size=downloaded_size
                )
            
            # Final memory check
            final_memory = get_memory_usage()
            processing_time = time.time() - start_time
            
            logger.info(f"Conversion completed successfully in {processing_time:.2f}s")
            logger.info(f"Final memory usage: {final_memory['rss_mb']:.2f}MB")
            
            return ConvertResponse(
                success=True,
                markdown=markdown_content,
                file_type=file_ext or "unknown",
                processing_time=processing_time,
                file_size=downloaded_size
            )
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error downloading file: {e}")
            return ConvertResponse(
                success=False,
                error=f"Failed to download file: HTTP {e.response.status_code}",
                processing_time=time.time() - start_time
            )
        except httpx.RequestError as e:
            logger.error(f"Request error downloading file: {e}")
            return ConvertResponse(
                success=False,
                error=f"Failed to download file: Connection error",
                processing_time=time.time() - start_time
            )
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return ConvertResponse(
                success=False,
                error=str(e),
                processing_time=time.time() - start_time
            )
        except asyncio.TimeoutError as e:
            logger.error(f"Timeout error: {e}")
            return ConvertResponse(
                success=False,
                error="Conversion timed out",
                processing_time=time.time() - start_time
            )
        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            return ConvertResponse(
                success=False,
                error=f"Conversion failed: {str(e)}",
                processing_time=time.time() - start_time
            )
        finally:
            # Clean up temp file
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                    logger.info("Temporary file cleaned up")
                except Exception as e:
                    logger.warning(f"Failed to clean up temp file: {e}")
                
    except Exception as e:
        logger.error(f"Request processing failed: {e}")
        return ConvertResponse(
            success=False,
            error=f"Request processing failed: {str(e)}",
            processing_time=time.time() - start_time
        )

# For AWS Lambda
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    from mangum import Mangum
    handler = Mangum(app)
    return handler(event, context)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)