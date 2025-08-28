"""
Utility functions for file handling, memory monitoring, and validation
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import magic
import psutil
import logging
from typing import Dict, Optional

from config import SUPPORTED_MIME_TYPES, FILE_TYPE_MAPPING

logger = logging.getLogger(__name__)

def validate_file_type(file_content: bytes) -> Optional[str]:
    """Validate file type using magic bytes and return MIME type"""
    try:
        mime_type = magic.from_buffer(file_content, mime=True)
        return mime_type if mime_type in SUPPORTED_MIME_TYPES else None
    except Exception as e:
        logger.warning(f"Magic byte detection failed: {e}")
        return None

def get_memory_usage() -> Dict[str, float]:
    """Get current memory usage statistics"""
    process = psutil.Process()
    memory_info = process.memory_info()
    return {
        "rss_mb": memory_info.rss / 1024 / 1024,  # Resident Set Size
        "vms_mb": memory_info.vms / 1024 / 1024,  # Virtual Memory Size
        "percent": process.memory_percent()
    }

def get_file_extension_from_mime(mime_type: str) -> str:
    """Get file extension from MIME type"""
    return FILE_TYPE_MAPPING.get(mime_type, "unknown")