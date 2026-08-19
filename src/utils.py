#!/usr/bin/env python3
"""
Utility Functions for Traceroute
Student: Asanul Hoque Sohan
ID: 2202038
"""

import socket
import sys
import time
from typing import Optional

def resolve_hostname(hostname: str) -> Optional[str]:
    """
    Resolve hostname to IP address.
    
    Args:
        hostname: Hostname or IP address
        
    Returns:
        str: Resolved IP address or None
    """
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        return None

def reverse_lookup(ip: str) -> str:
    """
    Perform reverse DNS lookup.
    
    Args:
        ip: IP address
        
    Returns:
        str: Hostname or IP if not resolved
    """
    try:
        hostname, _, _ = socket.gethostbyaddr(ip)
        return hostname
    except socket.herror:
        return ip
    except socket.gaierror:
        return ip

def is_valid_ip(ip: str) -> bool:
    """
    Check if string is a valid IP address.
    
    Args:
        ip: IP address string
        
    Returns:
        bool: True if valid IP
    """
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False

def format_rtt(rtt: float) -> str:
    """
    Format RTT value for display.
    
    Args:
        rtt: RTT in milliseconds
        
    Returns:
        str: Formatted RTT string
    """
    if rtt < 1:
        return f"{rtt:.3f}ms"
    elif rtt < 10:
        return f"{rtt:.2f}ms"
    else:
        return f"{rtt:.1f}ms"

def get_timestamp() -> str:
    """
    Get current timestamp as string.
    
    Returns:
        str: Formatted timestamp
    """
    return time.strftime("%Y-%m-%d %H:%M:%S")

def print_header(title: str, width: int = 80) -> None:
    """
    Print formatted header.
    
    Args:
        title: Header title
        width: Width of header
    """
    print("=" * width)
    print(f"{title.center(width)}")
    print("=" * width)

def check_privileges() -> bool:
    """
    Check if running with sufficient privileges.
    
    Returns:
        bool: True if running as root/admin
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        sock.close()
        return True
    except PermissionError:
        return False