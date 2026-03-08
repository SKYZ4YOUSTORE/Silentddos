#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import random
import threading
import queue
import time
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, Style
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ProxyEngine:
    def __init__(self, proxy_file=None):
        self.proxies = []
        self.working_proxies = []
        self.lock = threading.Lock()
        
        if proxy_file:
            self.load_proxies(proxy_file)
            
    def load_proxies(self, filename):
        """Load proxy dari file"""
        try:
            with open(filename, 'r') as f:
                self.proxies = [line.strip() for line in f if line.strip()]
        except:
            self.proxies = []
            
    def get_random_proxy(self):
        """Ambil random proxy"""
        if not self.proxies:
            return None
        return random.choice(self.proxies)
        
    def test_proxy(self, proxy, timeout=5):
        """Test proxy apakah working"""
        try:
            proxies = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
            
            # Test dengan multiple sites
            test_urls = [
                'http://httpbin.org/ip',
                'http://api.ipify.org',
                'http://checkip.amazonaws.com'
            ]
            
            for url in test_urls:
                try:
                    resp = requests.get(url, proxies=proxies, timeout=timeout, verify=False)
                    if resp.status_code == 200:
                        with self.lock:
                            self.working_proxies.append(proxy)
                        return True
                except:
                    continue
                    
        except:
            pass
            
        return False
        
    def test_proxies(self, filename=None, max_workers=100):
        """Test semua proxy"""
        if filename:
            self.load_proxies(filename)
            
        if not self.proxies:
            print(f"{Fore.RED}[!] Tidak ada proxy untuk di-test")
            return
            
        print(f"{Fore.YELLOW}[*] Testing {len(self.proxies)} proxies...")
        
        self.working_proxies = []
        total = len(self.proxies)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for proxy in self.proxies:
                futures.append(executor.submit(self.test_proxy, proxy))
                
            # Progress
            completed = 0
            for future in futures:
                future.result()
                completed += 1
                progress = (completed / total) * 100
                print(f"\r{Fore.CYAN}[{completed}/{total}] {progress:.1f}%", end='')
                
        print(f"\n{Fore.GREEN}[+] Found {len(self.working_proxies)} working proxies")
        
        # Save working proxies
        if self.working_proxies:
            with open('data/working_proxies.txt', 'w') as f:
                for proxy in self.working_proxies:
                    f.write(f"{proxy}\n")
                    
    @staticmethod
    def generate_proxy_list(count=100, output_file='data/proxies.txt'):
        """Generate proxy list dari sumber online"""
        print(f"{Fore.YELLOW}[*] Generating {count} proxies...")
        
        # Sumber proxy (dalam implementasi real, tambahkan lebih banyak sources)
        proxy_sources = [
            'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all',
            'https://www.proxy-list.download/api/v1/get?type=http',
            'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
        ]
        
        all_proxies = set()
        
        for source in proxy_sources:
            try:
                resp = requests.get(source, timeout=10)
                if resp.status_code == 200:
                    proxies = resp.text.split('\n')
                    for proxy in proxies:
                        proxy = proxy.strip()
                        if proxy and ':' in proxy:
                            all_proxies.add(proxy)
                            
                    if len(all_proxies) >= count:
                        break
            except:
                continue
                
        # Jika masih kurang, generate random
        while len(all_proxies) < count:
            ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
            port = random.choice([80, 8080, 3128, 8888, 1080])
            all_proxies.add(f"{ip}:{port}")
            
        # Save ke file
        with open(output_file, 'w') as f:
            for proxy in list(all_proxies)[:count]:
                f.write(f"{proxy}\n")
                
        print(f"{Fore.GREEN}[+] Generated {len(all_proxies)} proxies to {output_file}")