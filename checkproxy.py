import threading
import socket
import socks
import requests
import time
import os
from queue import Queue
from colorama import Fore, init, Style

init(autoreset=True)

BANNER = f"""
{Fore.RED}██████╗ ██████╗  ██████╗ ██╗  ██╗██╗   ██╗     ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗███████╗██████╗ 
{Fore.YELLOW}██╔══██╗██╔══██╗██╔═══██╗╚██╗██╔╝╚██╗ ██╔╝    ██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝██╔════╝██╔══██╗
{Fore.GREEN}██████╔╝██████╔╝██║   ██║ ╚███╔╝  ╚████╔╝     ██║     ███████║█████╗  ██║     █████╔╝ █████╗  ██████╔╝
{Fore.BLUE}██╔═══╝ ██╔══██╗██║   ██║ ██╔██╗   ╚██╔╝      ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ ██╔══╝  ██╔══██╗
{Fore.MAGENTA}██║     ██║  ██║╚██████╔╝██╔╝ ██╗   ██║       ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗███████╗██║  ██║
{Fore.CYAN}╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝        ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
{Style.RESET_ALL}
{Fore.WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{Fore.GREEN}                SILENT PROXY CHECKER - BY MR.SILENT🥶💀
{Fore.WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

TEST_URL = "http://httpbin.org/ip"
TIMEOUT = 10
THREAD_COUNT = 2000

input_file = "data/proxies.txt"
active_file = "proxy/proxy_active.txt"
dead_file = "proxy/proxy_dead.txt"

proxy_queue = Queue()
active_proxies = []
dead_proxies = []
lock = threading.Lock()
checked = 0
total = 0

def test_proxy(proxy):
    global checked
    proxy_str = proxy.strip()
    if not proxy_str:
        return

    try:
        # Parse proxy
        if "://" in proxy_str:
            proto, addr = proxy_str.split("://", 1)
        else:
            proto = "http"
            addr = proxy_str

        ip_port = addr.split(":")
        if len(ip_port) != 2:
            return
        ip, port = ip_port[0], int(ip_port[1])
        port = int(port)

        # Set proxy
        if proto.startswith("socks4"):
            socks.set_default_proxy(socks.SOCKS4, ip, port)
        elif proto.startswith("socks5"):
            socks.set_default_proxy(socks.SOCKS5, ip, port)
        else:
            # HTTP/HTTPS
            proxies = {
                "http": f"http://{ip}:{port}",
                "https": f"http://{ip}:{port}"
            }
            r = requests.get(TEST_URL, proxies=proxies, timeout=TIMEOUT)
            if r.status_code == 200:
                with lock:
                    active_proxies.append(proxy_str)
                    print(Fore.GREEN + f"[✓] ACTIVE: {proxy_str}")
                return
            else:
                with lock:
                    dead_proxies.append(proxy_str)
                    print(Fore.RED + f"[✗] DEAD: {proxy_str}")
                return

        # SOCKS test
        s = socks.socksocket()
        s.settimeout(TIMEOUT)
        s.connect(("httpbin.org", 80))
        s.send(b"GET /ip HTTP/1.1\r\nHost: httpbin.org\r\n\r\n")
        response = s.recv(1024)
        if b"200" in response:
            with lock:
                active_proxies.append(proxy_str)
                print(Fore.GREEN + f"[✓] ACTIVE: {proxy_str}")
        else:
            with lock:
                dead_proxies.append(proxy_str)
                print(Fore.RED + f"[✗] DEAD: {proxy_str}")
        s.close()

    except Exception as e:
        with lock:
            dead_proxies.append(proxy_str)
            print(Fore.RED + f"[✗] DEAD: {proxy_str} | {str(e)[:30]}...")
    finally:
        with lock:
            checked += 1
            progress = (checked / total) * 100 if total > 0 else 0
            print(Fore.CYAN + f"[~] Progress: {checked}/{total} ({progress:.1f}%)", end="\r")

def worker():
    while not proxy_queue.empty():
        try:
            proxy = proxy_queue.get_nowait()
            test_proxy(proxy)
        except:
            break

def main():
    global total
    print(BANNER)

    # Cek file input
    if not os.path.exists(input_file):
        print(Fore.RED + f"[-] File {input_file} gak ditemukan!")
        return

    # Baca proxy
    with open(input_file, "r") as f:
        proxies = [line.strip() for line in f if line.strip()]
    
    total = len(proxies)
    print(Fore.YELLOW + f"[!] Total proxy: {total} | Thread: {THREAD_COUNT} | Timeout: {TIMEOUT}s")
    print(Fore.WHITE + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # Masukin ke queue
    for proxy in proxies:
        proxy_queue.put(proxy)

    # Start worker threads
    threads = []
    for _ in range(min(THREAD_COUNT, total)):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    # Simpan hasil
    with open(active_file, "w") as f:
        f.write("\n".join(active_proxies))
    
    with open(dead_file, "w") as f:
        f.write("\n".join(dead_proxies))

    print("\n" + Fore.WHITE + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(Fore.GREEN + f"[✓] PROXY AKTIF: {len(active_proxies)} -> disimpan di {active_file}")
    print(Fore.RED + f"[✗] PROXY MATI: {len(dead_proxies)} -> disimpan di {dead_file}")
    print(Fore.WHITE + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    main()