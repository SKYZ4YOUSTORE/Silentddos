#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import random
import time
import socket
from colorama import Fore, Style, init

init(autoreset=True)

USER_AGENTS = []

def load_useragents():
    """Load useragents dari file"""
    global USER_AGENTS
    try:
        with open('data/useragents.txt', 'r') as f:
            USER_AGENTS = [line.strip() for line in f if line.strip()]
    except:
        # Default useragents jika file tidak ada
        USER_AGENTS = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
        ]

def get_random_useragent():
    """Ambil random useragent"""
    if not USER_AGENTS:
        load_useragents()
    return random.choice(USER_AGENTS)

def get_random_proxy(proxy_list):
    """Ambil random proxy dari list"""
    if proxy_list:
        return random.choice(proxy_list)
    return None

def validate_ip(ip):
    """Validasi format IP"""
    try:
        socket.inet_aton(ip)
        return True
    except:
        return False

def validate_url(url):
    """Validasi URL"""
    return url.startswith(('http://', 'https://'))

def print_banner():
    """Print banner tool"""
    banner = f"""
{Fore.RED}
╔╦╗╦ ╦╔╦╗╔╦╗╦  ╔╦╗  ╔╗╔╔╦╗╔╦╗╔═╗╦╔╗╔╔═╗
 ║ ╠═╣║║║║║║║   ║║  ║║║ ║║ ║║╠═╣║║║║╚═╗
 ╩ ╩ ╩╩ ╩╩ ╩╩═╝═╩╝  ╝╚╝═╩╝═╩╝╩ ╩╩╝╚╝╚═╝
{Fore.YELLOW}
╔══════════════════════════════════════════════════════════╗
║                DDoS Mr. Voidsz - Ultimate Tool            ║
║                 Created by Voidsz_GPT 🔥                  ║
║            Project ShadowKeep Escape Build               ║
╚══════════════════════════════════════════════════════════╝
{Fore.CYAN}
     Layer 7 & Layer 4 Attack Methods | Bypass Protection
{Style.RESET_ALL}
    """
    print(banner)

def loading_animation(text="Loading", delay=0.1):
    """Loading animation"""
    animation = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    
    for i in range(20):
        print(f"\r{Fore.CYAN}{text} {animation[i % len(animation)]}", end="")
        time.sleep(delay)
    print()