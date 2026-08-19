#!/usr/bin/env python3
"""
ICMP Packet Helper Module
Student: Asanul Hoque Sohan
ID: 2202038
"""

import struct
import socket
import time
from typing import Tuple, Optional

def calculate_checksum(data: bytes) -> int:
    """
    Calculate ICMP checksum.
    
    Args:
        data: Raw packet data
        
    Returns:
        int: Calculated checksum
    """
    if len(data) % 2 != 0:
        data += b'\x00'
    
    checksum = 0
    for i in range(0, len(data), 2):
        word = (data[i] << 8) + data[i + 1]
        checksum += word
    
    checksum = (checksum >> 16) + (checksum & 0xFFFF)
    checksum = ~checksum & 0xFFFF
    
    return checksum

def build_icmp_echo(identifier: int, sequence: int) -> bytes:
    """
    Build ICMP Echo Request packet.
    
    Args:
        identifier: ICMP identifier
        sequence: Sequence number
        
    Returns:
        bytes: ICMP packet
    """
    icmp_type = 8  # Echo Request
    icmp_code = 0
    checksum = 0
    
    # Timestamp payload
    timestamp = struct.pack('!d', time.time())
    
    # Build packet without checksum
    packet = struct.pack('!BBHHH', icmp_type, icmp_code, 
                        checksum, identifier, sequence) + timestamp
    
    # Calculate checksum
    checksum = calculate_checksum(packet)
    
    # Rebuild with correct checksum
    packet = struct.pack('!BBHHH', icmp_type, icmp_code, 
                        checksum, identifier, sequence) + timestamp
    
    return packet

def parse_icmp_response(data: bytes) -> Tuple[int, int, str, float]:
    """
    Parse ICMP response packet.
    
    Args:
        data: Raw response data
        
    Returns:
        Tuple: (icmp_type, icmp_code, source_ip, receive_time)
    """
    # Extract source IP from IP header
    ip_header = data[:20]
    source_ip = socket.inet_ntoa(ip_header[12:16])
    
    # IP header length
    ip_header_len = (ip_header[0] & 0x0F) * 4
    
    # ICMP starts after IP header
    icmp_data = data[ip_header_len:]
    
    # Parse ICMP header
    icmp_type, icmp_code, checksum, identifier, sequence = struct.unpack(
        '!BBHHH', icmp_data[:8])
    
    # Parse timestamp
    timestamp = struct.unpack('!d', icmp_data[8:16])[0]
    receive_time = time.time()
    
    return icmp_type, icmp_code, source_ip, receive_time

def parse_icmp_type(type_code: int) -> str:
    """
    Get human-readable ICMP type description.
    
    Args:
        type_code: ICMP type number
        
    Returns:
        str: Description of ICMP type
    """
    types = {
        0: "Echo Reply",
        3: "Destination Unreachable",
        4: "Source Quench",
        5: "Redirect",
        8: "Echo Request",
        9: "Router Advertisement",
        10: "Router Solicitation",
        11: "Time Exceeded",
        12: "Parameter Problem",
        13: "Timestamp Request",
        14: "Timestamp Reply",
        15: "Information Request",
        16: "Information Reply"
    }
    return types.get(type_code, f"Unknown ({type_code})")