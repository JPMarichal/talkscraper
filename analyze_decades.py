#!/usr/bin/env python3
"""
Script temporal para analizar la estructura de páginas de décadas
"""

import requests
from bs4 import BeautifulSoup

def analyze_decade_page():
    url = 'https://www.churchofjesuschrist.org/study/general-conference/20102019?lang=eng'
    print(f"Analizando: {url}")
    
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    print('\n=== Enlaces con portrait ===')
    portrait_links = soup.select('a.portrait-jkaM1')
    for i, link in enumerate(portrait_links[:10]):
        href = link.get('href')
        text = link.get_text().strip()[:50]
        print(f'{i+1}. {href} - {text}')
    print(f'Total portrait-jkaM1: {len(portrait_links)}')
    
    print('\n=== Enlaces de conferencia general ===')
    conf_links = soup.select('a[href*="/study/general-conference/"]')
    for i, link in enumerate(conf_links[:15]):
        href = link.get('href')
        text = link.get_text().strip()[:50]
        print(f'{i+1}. {href} - {text}')
    print(f'Total conferencia: {len(conf_links)}')
    
    print('\n=== Verificando otras páginas de década ===')
    
    # Verificar también otras décadas
    other_decades = [
        'https://www.churchofjesuschrist.org/study/general-conference/19702009?lang=eng',
        'https://www.churchofjesuschrist.org/study/general-conference/19712019?lang=eng'
    ]
    
    for decade_url in other_decades:
        print(f'\n--- Analizando {decade_url} ---')
        try:
            resp = requests.get(decade_url)
            soup_decade = BeautifulSoup(resp.content, 'html.parser')
            decade_portraits = soup_decade.select('a.portrait-jkaM1')
            print(f'Enlaces portrait en esta década: {len(decade_portraits)}')
            
            if decade_portraits:
                print('Primeros 3 enlaces:')
                for i, link in enumerate(decade_portraits[:3]):
                    href = link.get('href')
                    text = link.get_text().strip()[:30]
                    print(f'  {i+1}. {href} - {text}')
        except Exception as e:
            print(f'Error analizando {decade_url}: {e}')

if __name__ == '__main__':
    analyze_decade_page()
