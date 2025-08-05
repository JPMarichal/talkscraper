#!/usr/bin/env python3
"""
Script para encontrar las URLs correctas de páginas de décadas
"""

import requests
from bs4 import BeautifulSoup

def find_decade_pages():
    # Verificar la página principal para encontrar enlaces a páginas de décadas
    main_url = 'https://www.churchofjesuschrist.org/study/general-conference?lang=eng'
    response = requests.get(main_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    print('=== Buscando enlaces a décadas en página principal ===')
    # Buscar enlaces que puedan contener rangos de años
    all_links = soup.find_all('a', href=True)
    decade_candidates = []
    
    for link in all_links:
        href = link.get('href')
        text = link.get_text().strip()
        
        # Buscar patrones que indiquen décadas
        if ('2010' in href or '1990' in href or '1980' in href or '1970' in href or 
            '2019' in href or '2009' in href or '1999' in href or '1989' in href):
            decade_candidates.append((href, text))

    for href, text in decade_candidates[:10]:
        print(f'{href} - {text}')

    print('\n=== Probando URLs conocidas de décadas ===')
    test_urls = [
        'https://www.churchofjesuschrist.org/study/general-conference/20102019?lang=eng',
        'https://www.churchofjesuschrist.org/study/general-conference/20002009?lang=eng',
        'https://www.churchofjesuschrist.org/study/general-conference/19902009?lang=eng',
        'https://www.churchofjesuschrist.org/study/general-conference/19801989?lang=eng',
        'https://www.churchofjesuschrist.org/study/general-conference/19701979?lang=eng',
        'https://www.churchofjesuschrist.org/study/general-conference/19711980?lang=eng'
    ]

    valid_decades = []
    for url in test_urls:
        try:
            resp = requests.get(url)
            print(f'{url} - Status: {resp.status_code}')
            if resp.status_code == 200:
                soup_test = BeautifulSoup(resp.content, 'html.parser')
                portraits = soup_test.select('a.portrait-jkaM1')
                print(f'  -> {len(portraits)} conferencias encontradas')
                if len(portraits) > 0:
                    valid_decades.append(url)
        except Exception as e:
            print(f'{url} - Error: {e}')
    
    print(f'\n=== URLs válidas de décadas encontradas ===')
    for url in valid_decades:
        print(url)

if __name__ == '__main__':
    find_decade_pages()
