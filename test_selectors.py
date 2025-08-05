#!/usr/bin/env python3
"""
Script para probar selectores CSS específicos.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sys

def test_css_selectors(url):
    """Probar diferentes selectores CSS."""
    
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    print(f"🔍 Probando selectores en: {url}")
    
    # Probar selector más específico basado en las clases CSS encontradas
    selectors = [
        'nav ul li a',
        'ul li a[href*="/study/general-conference/"]',
        'a[href*="/study/general-conference/"]:not([href*="session"])',
        'div.sc-omeqik-7 a',
        'div.iwWCCo a',
        'nav a[href*="/study/general-conference/"]'
    ]
    
    for selector in selectors:
        try:
            links = soup.select(selector)
            print(f'\nSelector "{selector}": {len(links)} enlaces')
            
            # Filtrar enlaces de discursos individuales
            talk_links = []
            for link in links:
                href = link.get('href', '')
                if href and '/study/general-conference/' in href:
                    parts = href.split('/')
                    if len(parts) >= 6 and 'session' not in href:
                        full_url = urljoin(url, href)
                        talk_links.append(full_url)
            
            print(f'  Enlaces de discursos filtrados: {len(talk_links)}')
            if talk_links:
                print(f'  Primeros 3:')
                for i, link in enumerate(talk_links[:3]):
                    print(f'    {i+1}. {link}')
        except Exception as e:
            print(f'  Error con selector: {e}')

if __name__ == "__main__":
    test_url = "https://conference.lds.org/study/general-conference/2022/10?lang=spa"
    
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    
    test_css_selectors(test_url)
