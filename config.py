"""
Configuration constants and settings
"""
import ipaddress
from typing import Dict, Set

# File type mappings using magic numbers
FILE_TYPE_MAPPING = {
    'application/pdf': '.pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
    'text/html': '.html',
    'text/plain': '.txt',
    'text/rtf': '.rtf',
    'text/csv': '.csv',
    'application/json': '.json',
    'application/xml': '.xml',
    'text/xml': '.xml',
    'application/zip': '.zip',
    'application/epub+zip': '.epub',
    'image/jpeg': '.jpg',
    'image/png': '.png',
    'image/gif': '.gif'
}

SUPPORTED_MIME_TYPES = set(FILE_TYPE_MAPPING.keys())

# SSRF Protection Configuration
BLOCKED_HOSTS = {
    'localhost', '0.0.0.0', '127.0.0.1',
    '169.254.169.254',  # AWS/Azure metadata
    'metadata.google.internal',  # Google Cloud metadata
    'metadata', 'metadata.azure.com'  # Additional metadata endpoints
}

BLOCKED_NETWORKS = [
    ipaddress.IPv4Network('127.0.0.0/8'),      # Loopback
    ipaddress.IPv4Network('10.0.0.0/8'),       # Private Class A
    ipaddress.IPv4Network('172.16.0.0/12'),    # Private Class B
    ipaddress.IPv4Network('192.168.0.0/16'),   # Private Class C
    ipaddress.IPv4Network('169.254.0.0/16'),   # Link-local
    ipaddress.IPv4Network('224.0.0.0/4'),      # Multicast
    ipaddress.IPv4Network('240.0.0.0/4'),      # Reserved
    ipaddress.IPv6Network('::1/128'),          # IPv6 loopback
    ipaddress.IPv6Network('fc00::/7'),         # IPv6 private
    ipaddress.IPv6Network('fe80::/10'),        # IPv6 link-local
]

ALLOWED_PORTS = {80, 443, 8080, 8443}  # Only allow standard HTTP/HTTPS ports

# Application settings
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_MEMORY_INCREASE = 500  # 500MB
DOWNLOAD_TIMEOUT = 30  # seconds
CONVERSION_TIMEOUT = 120  # seconds
CHUNK_SIZE = 8192  # bytes

# HTTP client settings
MAX_CONNECTIONS = 20
MAX_KEEPALIVE_CONNECTIONS = 10
HTTP_TIMEOUT = 30.0  # seconds

USER_AGENT = "MarkItDown-Service/1.0"