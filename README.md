# Traceroute Implementation in Python

## Student Information
- **Name:** Asanul Hoque Sohan
- **ID:** 2202038
- **Reg:** 11229
- **Course:** CCE 314 - Computer Networks Sessional Lab
- **Instructor:** Dr. Md Samsuzzaman Sobuz

## Project Description
This project implements a complete traceroute tool using Python and ICMP protocol. It traces the network path from source to destination, displaying each hop with IP addresses and round-trip times.

## Features
- ICMP-based traceroute implementation
- Hostname resolution for each hop
- Configurable parameters (max hops, timeout, probes)
- Real-time round-trip time measurement
- Multi-probe for reliability
- Clean command-line interface
- Error handling and timeout management

## Requirements
- Python 3.6 or higher
- Root/Administrator privileges (for raw socket creation)

## Installation

### Linux/Mac/Windows
```bash
# Clone the repository
git clone https://github.com/AsanulSohan/Traceroute-Implementation-Python.git

# Navigate to project directory
cd traceroute-project

# Make script executable
chmod +x src/traceroute.py