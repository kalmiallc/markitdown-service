"""
Security utilities for SSRF protection and URL validation
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import socket
import ipaddress
import logging
from typing import Optional
from urllib.parse import urlparse

from config import BLOCKED_HOSTS, BLOCKED_NETWORKS, ALLOWED_PORTS

logger = logging.getLogger(__name__)

def validate_ip_address(ip_str: str) -> bool:
    """Validate that an IP address is not in blocked networks"""
    try:
        ip = ipaddress.ip_address(ip_str)
        
        # Check against blocked networks
        for network in BLOCKED_NETWORKS:
            if ip in network:
                return False
                
        # Additional checks for dangerous addresses
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast:
            return False
            
        return True
    except ValueError:
        return False

def resolve_hostname_safely(hostname: str) -> Optional[str]:
    """Safely resolve hostname and validate the resulting IP"""
    try:
        # Get all IP addresses for the hostname
        addr_info = socket.getaddrinfo(hostname, None)
        
        for family, type, proto, canonname, sockaddr in addr_info:
            ip = sockaddr[0]
            
            # IPv6 addresses might be in brackets, remove them
            if ip.startswith('[') and ip.endswith(']'):
                ip = ip[1:-1]
                
            # Validate each resolved IP
            if not validate_ip_address(ip):
                logger.warning(f"Blocked IP resolution: {hostname} -> {ip}")
                return None
                
        return hostname  # All IPs are safe
        
    except (socket.gaierror, socket.error) as e:
        logger.error(f"DNS resolution failed for {hostname}: {e}")
        return None

def validate_url_security(url: str) -> tuple[bool, str]:
    """Comprehensive URL security validation to prevent SSRF attacks"""
    try:
        parsed = urlparse(url)
        
        # Check scheme
        if parsed.scheme not in ['http', 'https']:
            return False, f"Invalid scheme: {parsed.scheme}. Only http/https allowed."
        
        # Check port
        port = parsed.port
        if port and port not in ALLOWED_PORTS:
            return False, f"Port {port} not allowed. Only ports {ALLOWED_PORTS} are permitted."
        
        hostname = parsed.hostname
        if not hostname:
            return False, "Invalid URL: missing hostname"
        
        # Check for blocked hostnames
        hostname_lower = hostname.lower()
        if hostname_lower in BLOCKED_HOSTS:
            return False, f"Blocked hostname: {hostname}"
        
        # Check for obvious localhost variations
        localhost_variations = ['localhost', '127.0.0.1', '0.0.0.0', '::1']
        if hostname_lower in localhost_variations:
            return False, f"Localhost access blocked: {hostname}"
        
        # If hostname is an IP address, validate directly
        if hostname.replace('.', '').replace(':', '').isdigit() or ':' in hostname:
            try:
                # Try to parse as IP address
                if not validate_ip_address(hostname):
                    return False, f"Blocked IP address: {hostname}"
            except:
                pass  # Not a valid IP, continue with hostname resolution
        
        # Resolve hostname and validate resulting IPs
        if not resolve_hostname_safely(hostname):
            return False, f"Hostname resolution failed or resolved to blocked IP: {hostname}"
        
        # Additional URL pattern checks
        if any(blocked in hostname_lower for blocked in ['metadata', 'internal']):
            return False, f"Suspicious hostname pattern detected: {hostname}"
        
        return True, "URL validation passed"
        
    except Exception as e:
        return False, f"URL validation error: {str(e)}"