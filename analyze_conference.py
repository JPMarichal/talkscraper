#!/usr/bin/env python3
"""
Script para analizar la estructura de páginas de conferencias
"""

import requests
from bs4 import BeautifulSoup

def analyze_conference_structure():
    # Analizar una conferencia reciente para entender la estructura
    url = 'https://www.churchofjesuschrist.org/study/general-conference/2024/04?lang=eng'
    print(f'Analizando: {url}')

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    print('\n=== Buscando discursos con selector configurado ===')
    talk_selector = 'li[data-content-type="general-conference-talk"] a'
    talks = soup.select(talk_selector)
    print(f'Discursos encontrados con selector actual: {len(talks)}')

    if talks:
        print('\nPrimeros 5 discursos:')
        for i, talk in enumerate(talks[:5]):
            href = talk.get('href')
            title = talk.get_text().strip()
            print(f'  {i+1}. {href} - {title[:50]}...')
    else:
        print('\n=== Buscando otros patrones ===')
        # Buscar otros patrones posibles
        patterns = [
            'a[href*="/study/general-conference/"][href*="?"]',
            'li[data-content-type] a',
            'article a',
            '.tile a',
            'ul li a[href*="/study/general-conference/"]'
        ]
        
        for pattern in patterns:
            elements = soup.select(pattern)
            print(f'{pattern}: {len(elements)} elementos')
            if elements and len(elements) < 50:  # Si no son demasiados
                for i, elem in enumerate(elements[:3]):
                    href = elem.get('href') or 'N/A'
                    text = elem.get_text().strip()[:30]
                    print(f'  {i+1}. {href} - {text}')
            print()

if __name__ == '__main__':
    analyze_conference_structure()
