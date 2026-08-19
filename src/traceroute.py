#!/usr/bin/env python3
"""
Traceroute Implementation Using Python
Student: Asanul Hoque Sohan
ID: 2202038
Course: CCE 314 - Computer Networks Lab
"""

import socket
import struct
import time
import sys
import os
import argparse
import select
from typing import Optional, List, Tuple

class Traceroute:
    """
    Main Traceroute class implementing ICMP-based route tracing.
    """
    
    def __init__(self, destination: str, max_hops: int = 30, 
                 timeout: float = 1.0, probes_per_hop: int = 3):
        """
        Initialize Traceroute with parameters.
        
        Args:
            destination: Target hostname or IP address
            max_hops: Maximum number of hops to trace
            timeout: Timeout in seconds for each probe
            probes_per_hop: Number of probes to send per hop
        """
        self.destination = destination
        self.max_hops = max_hops
        self.timeout = timeout
        self.probes_per_hop = probes_per_hop
        self.dest_ip = None
        self.sock = None
        self.packet_id = os.getpid() & 0xFFFF
        
        # Resolve destination
        self._resolve_destination()
        
    def _resolve_destination(self) -> None:
        """
        Resolve hostname to IP address.
        """
        try:
            self.dest_ip = socket.gethostbyname(self.destination)
            print(f"Traceroute to {self.destination} ({self.dest_ip})")
            print(f"Max hops: {self.max_hops}, Timeout: {self.timeout}s")
            print("-" * 60)
        except socket.gaierror:
            print(f"Error: Could not resolve hostname '{self.destination}'")
            sys.exit(1)
    
    def _create_icmp_packet(self, sequence: int) -> bytes:
        """
        Create an ICMP Echo Request packet.
        
        Args:
            sequence: Sequence number for the probe
            
        Returns:
            bytes: Raw ICMP packet
        """
        # ICMP Echo Request: Type=8, Code=0
        icmp_type = 8
        icmp_code = 0
        
        # ICMP header fields
        checksum = 0
        identifier = self.packet_id
        
        # Timestamp payload (8 bytes)
        timestamp = struct.pack('!d', time.time())
        
        # Build ICMP packet without checksum
        icmp_packet = struct.pack('!BBHHH', icmp_type, icmp_code, 
                                  checksum, identifier, sequence) + timestamp
        
        # Calculate checksum
        checksum = self._calculate_checksum(icmp_packet)
        
        # Rebuild with correct checksum
        icmp_packet = struct.pack('!BBHHH', icmp_type, icmp_code, 
                                  checksum, identifier, sequence) + timestamp
        
        return icmp_packet
    
    def _calculate_checksum(self, data: bytes) -> int:
        """
        Calculate ICMP checksum.
        
        Args:
            data: Raw packet data
            
        Returns:
            int: Calculated checksum
        """
        # Ensure even length
        if len(data) % 2 != 0:
            data += b'\x00'
        
        checksum = 0
        for i in range(0, len(data), 2):
            word = (data[i] << 8) + data[i + 1]
            checksum += word
        
        checksum = (checksum >> 16) + (checksum & 0xFFFF)
        checksum = ~checksum & 0xFFFF
        
        return checksum
    
    def _create_socket(self) -> None:
        """
        Create raw socket for ICMP communication.
        """
        try:
            # Create raw socket with ICMP protocol
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, 
                                      socket.IPPROTO_ICMP)
            # Set socket timeout
            self.sock.settimeout(self.timeout)
        except PermissionError:
            print("Error: Root/Administrator privileges required.")
            print("Run with: sudo python3 traceroute.py <destination>")
            sys.exit(1)
        except Exception as e:
            print(f"Error creating socket: {e}")
            sys.exit(1)
    
    def _send_probe(self, ttl: int, sequence: int) -> Tuple[float, bytes, str]:
        """
        Send a single ICMP probe.
        
        Args:
            ttl: Time-To-Live value
            sequence: Probe sequence number
            
        Returns:
            Tuple: (send_time, response, response_address)
        """
        # Set TTL
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
        
        # Create and send packet
        icmp_packet = self._create_icmp_packet(sequence)
        send_time = time.time()
        self.sock.sendto(icmp_packet, (self.dest_ip, 0))
        
        # Wait for response
        try:
            response, addr = self.sock.recvfrom(1024)
            return send_time, response, addr[0]
        except socket.timeout:
            return send_time, None, None
    
    def _parse_response(self, response: bytes) -> Tuple[int, int, float]:
        """
        Parse ICMP response packet.
        
        Args:
            response: Raw response packet
            
        Returns:
            Tuple: (icmp_type, icmp_code, receive_time)
        """
        # IP header is 20 bytes (minimum)
        # ICMP header starts after IP header
        ip_header_len = (response[0] & 0x0F) * 4
        icmp_data = response[ip_header_len:]
        
        # Parse ICMP header
        icmp_type, icmp_code, checksum, identifier, sequence = struct.unpack(
            '!BBHHH', icmp_data[:8])
        
        # Parse timestamp from payload
        timestamp = struct.unpack('!d', icmp_data[8:16])[0]
        receive_time = time.time()
        
        return icmp_type, icmp_code, receive_time
    
    def _get_hop_info(self, ttl: int) -> List[Tuple[str, str, Optional[float]]]:
        """
        Send probes for a single hop and gather results.
        
        Args:
            ttl: Current TTL value
            
        Returns:
            List of (status, address, rtt) tuples
        """
        results = []
        
        for i in range(self.probes_per_hop):
            send_time, response, addr = self._send_probe(ttl, i)
            
            if response is None:
                # Timeout
                results.append(("timeout", "*", None))
                continue
            
            # Parse response
            icmp_type, icmp_code, receive_time = self._parse_response(response)
            rtt = (receive_time - send_time) * 1000  # Convert to ms
            
            if icmp_type == 0:  # Echo Reply
                # Destination reached
                results.append(("destination", addr, rtt))
            elif icmp_type == 11:  # Time Exceeded
                results.append(("hop", addr, rtt))
            else:
                results.append(("unknown", addr, rtt))
        
        return results
    
    def _resolve_hostname(self, ip: str) -> str:
        """
        Reverse resolve IP to hostname.
        
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
    
    def _display_hop(self, ttl: int, results: List[Tuple[str, str, Optional[float]]]):
        """
        Display results for a hop.
        
        Args:
            ttl: Hop number
            results: List of (status, address, rtt) tuples
        """
        # Format hop number
        hop_str = f"{ttl:2d}"
        
        # Collect unique addresses
        addresses = set()
        rtts = []
        reached_destination = False
        
        for status, addr, rtt in results:
            if status == "destination":
                reached_destination = True
                addresses.add(addr)
                if rtt is not None:
                    rtts.append(rtt)
            elif status == "hop":
                addresses.add(addr)
                if rtt is not None:
                    rtts.append(rtt)
            elif status == "timeout":
                addresses.add("*")
        
        # Display address with hostname
        if len(addresses) == 1 and "*" in addresses:
            print(f"{hop_str}  *")
            return
        
        # Display with hostname resolution
        for addr in addresses:
            if addr != "*":
                hostname = self._resolve_hostname(addr)
                rtt_display = ""
                if rtts:
                    rtt_display = f"  {min(rtts):.2f}ms"
                print(f"{hop_str}  {hostname} ({addr}){rtt_display}")
                reached_destination = True
                break
        else:
            print(f"{hop_str}  *")
    
    def run(self) -> None:
        """
        Main execution method.
        """
        self._create_socket()
        
        print("\n" + "="*80)
        print("TRACEROUTE IMPLEMENTATION")
        print("="*80)
        print(f"Destination: {self.destination} ({self.dest_ip})")
        print(f"Max Hops: {self.max_hops}")
        print(f"Probes per hop: {self.probes_per_hop}")
        print(f"Timeout: {self.timeout}s")
        print("="*80)
        print("\n HOP   HOSTNAME / IP ADDRESS              RTT")
        print("-"*60)
        
        reached = False
        
        for ttl in range(1, self.max_hops + 1):
            results = self._get_hop_info(ttl)
            self._display_hop(ttl, results)
            
            # Check if destination reached
            for status, addr, _ in results:
                if status == "destination":
                    reached = True
                    break
            
            if reached:
                break
            
            # Rate limiting to avoid overwhelming network
            time.sleep(0.1)
        
        self.sock.close()
        
        print("-"*60)
        if reached:
            print("\n✓ Trace complete - Destination reached!")
        else:
            print(f"\n✗ Trace incomplete - Max hops ({self.max_hops}) reached")
        
        print(f"\nTraceroute completed for {self.destination}")


def main():
    """
    Command line interface for traceroute.
    """
    parser = argparse.ArgumentParser(
        description="Python Traceroute Implementation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sudo python3 traceroute.py google.com
  sudo python3 traceroute.py 8.8.8.8 --max-hops 20
  sudo python3 traceroute.py facebook.com --timeout 2.0 --probes 5
        """
    )
    
    parser.add_argument(
        "destination",
        help="Destination hostname or IP address"
    )
    parser.add_argument(
        "-m", "--max-hops",
        type=int,
        default=30,
        help="Maximum number of hops (default: 30)"
    )
    parser.add_argument(
        "-t", "--timeout",
        type=float,
        default=1.0,
        help="Timeout in seconds for each probe (default: 1.0)"
    )
    parser.add_argument(
        "-p", "--probes",
        type=int,
        default=3,
        help="Number of probes per hop (default: 3)"
    )
    
    args = parser.parse_args()
    
    # Create and run traceroute
    traceroute = Traceroute(
        destination=args.destination,
        max_hops=args.max_hops,
        timeout=args.timeout,
        probes_per_hop=args.probes
    )
    
    try:
        traceroute.run()
    except KeyboardInterrupt:
        print("\n\nTraceroute interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()