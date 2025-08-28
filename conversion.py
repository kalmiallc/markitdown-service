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
        # If OPEN_AI_BASE_URL is provided, configure a custom OpenAI client and model
        base_url = os.getenv("OPEN_AI_BASE_URL", "").strip()
        if base_url:
            api_key = os.getenv("OPEN_AI_API_KEY", "").strip()
            model = os.getenv("OPEN_AI_MODEL", "").strip() or None
            try:
                client = OpenAI(base_url=base_url, api_key=api_key)
                logger.info("Using custom OpenAI client for MarkItDown conversion (base_url provided)")
                md_converter = MarkItDown(llm_client=client, llm_model=model)
            except Exception as e:
                logger.warning(f"Failed to initialize custom OpenAI client, falling back to default MarkItDown: {e}")
                md_converter = MarkItDown()
        else:
            # Default behavior without custom LLM client
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
