"""
Pydantic models for request/response validation
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pydantic import BaseModel, HttpUrl, validator
from security import validate_url_security

class ConvertRequest(BaseModel):
    url: HttpUrl
    
    @validator('url')
    def validate_url_security_pydantic(cls, v):
        url_str = str(v)
        is_valid, error_message = validate_url_security(url_str)
        if not is_valid:
            raise ValueError(f'URL security validation failed: {error_message}')
        return v
    
class ConvertResponse(BaseModel):
    success: bool
    markdown: str = ""
    error: str = ""
    file_type: str = ""
    processing_time: float = 0.0
    file_size: int = 0