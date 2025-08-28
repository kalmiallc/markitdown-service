"""
Document conversion functionality using MarkItDown
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asyncio
import logging
from markitdown import MarkItDown

from config import CONVERSION_TIMEOUT

from openai import OpenAI

# client = OpenAI(api_key="")

logger = logging.getLogger(__name__)

async def convert_with_timeout(file_path: str, timeout: int = CONVERSION_TIMEOUT) -> str:
    """Convert file with timeout using thread pool"""
    loop = asyncio.get_event_loop()
    
    def convert_sync():
        """Synchronous conversion function to run in thread pool"""
        # md_converter = MarkItDown(llm_client=client, llm_model="gpt-4o")
        md_converter = MarkItDown()
        result = md_converter.convert(file_path)
        return result.text_content
    
    try:
        # Run conversion in thread pool with timeout
        result = await asyncio.wait_for(
            loop.run_in_executor(None, convert_sync),
            timeout=timeout
        )
        return result
    except asyncio.TimeoutError:
        logger.error(f"Conversion timed out after {timeout} seconds")
        raise Exception(f"Conversion timed out after {timeout} seconds")