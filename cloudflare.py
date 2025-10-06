import requests
import socket
from urllib.parse import urlparse
from colorama import Fore, Style, init
import json


def load_websites_json():
    """Carga la lista de sitios web desde un archivo JSON"""
    try:
        with open("websites.json", "r") as file:
            return json.load(file)
    except Exception as e:
        print(f"Error al cargar websites.json: {e}")
        return []


init(autoreset=True)  # Colores automáticos en consola


def uses_cloudflare(url):
    """Comprueba si la web usa Cloudflare según los headers"""
    try:
        response = requests.head(f"https://{url}", timeout=5, allow_redirects=True)
        headers = response.headers
        cf_headers = ["server", "cf-ray", "cf-cache-status"]
        for header in cf_headers:
            if header in headers and "cloudflare" in headers[header].lower():
                return True
        return False
    except requests.RequestException:
        return False


def get_ip(url):
    """Obtiene la IP mediante resolución DNS"""
    try:
        hostname = urlparse(url).hostname or url
        ip = socket.gethostbyname(hostname)
        return ip
    except Exception:
        return "No disponible"


def is_cf_ip(ip):
    """Comprueba si la IP empieza por el rango Cloudflare 188.114.9"""
    return ip.startswith("188.114.9")


if __name__ == "__main__":
    cloudflare_sites = []
    websites = load_websites_json()

    for site in websites:
        ip = get_ip(site)
        cf = uses_cloudflare(site)
        highlight = ""

        if ip != "No disponible" and is_cf_ip(ip):
            highlight = Fore.YELLOW + "[IP rango 188.114.9]" + Style.RESET_ALL

        if cf:
            print(f"{Fore.GREEN}[+] {site} usa Cloudflare | IP: {ip} {highlight}")
            cloudflare_sites.append((site, ip))
        else:
            print(
                f"{Fore.RED}[-] {site} no parece usar Cloudflare | IP: {ip} {highlight}"
            )

    print("\n" + Fore.CYAN + "Resumen: webs que usan Cloudflare:\n" + Style.RESET_ALL)
    for site, ip in cloudflare_sites:
        color = Fore.YELLOW if is_cf_ip(ip) else Fore.WHITE
        print(f"{color}{site} | IP: {ip}")
