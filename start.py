#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

# Pastikan path benar
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import main
from main import main

if __name__ == "__main__":
    # Check dependencies
    try:
        import requests
        import colorama
        print("[*] Dependencies OK")
    except ImportError:
        print("[!] Installing dependencies...")
        os.system("pip install -r requirements.txt")
    
    # Run main
    main()