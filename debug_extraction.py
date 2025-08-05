#!/usr/bin/env python3
"""
Script de diagnóstico para investigar por qué no se están encontrando discursos.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sys

def test_talk_extraction(url):
    """Probar extracción de discursos de una URL específica."""
    
    print(f"🔍 Probando extracción de discursos de: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Probar diferentes selectores CSS
        selectors_to_test = [
            'li[data-content-type="general-conference-talk"] a',
            'a[href*="/study/general-conference/"]',
            '.title-wrapper a',
            '.title a', 
            'h4 a',
            '.sc-fhYwyz a',
            'article a',
            '.content-meta a'
        ]
        
        print(f"\n📄 Página cargada exitosamente. Tamaño: {len(response.content)} bytes")
        
        for i, selector in enumerate(selectors_to_test, 1):
            try:
                links = soup.select(selector)
                print(f"\n{i}. Selector: '{selector}'")
                print(f"   Enlaces encontrados: {len(links)}")
                
                if links:
                    print("   Primeros 3 enlaces:")
                    for j, link in enumerate(links[:3]):
                        href = link.get('href', 'N/A')
                        text = link.get_text(strip=True)[:50] + "..." if len(link.get_text(strip=True)) > 50 else link.get_text(strip=True)
                        full_url = urljoin(url, href) if href != 'N/A' else 'N/A'
                        print(f"     {j+1}. {text}")
                        print(f"        href: {href}")
                        print(f"        full: {full_url}")
                        
                        # Verificar si parece una URL de discurso
                        if '/study/general-conference/' in href and len(href.split('/')) >= 6:
                            print(f"        ✅ Parece una URL de discurso válida")
                        else:
                            print(f"        ❌ No parece una URL de discurso")
                
            except Exception as e:
                print(f"   ❌ Error con selector: {e}")
        
        # Buscar manualmente elementos que contengan texto relacionado con discursos
        print(f"\n🔍 Búsqueda manual de elementos con texto de discursos:")
        
        # Buscar por patrones comunes
        talk_patterns = ['Discurso', 'Las bendiciones', 'Sesión', 'Gordon B.', 'Elder', 'Presidente']
        for pattern in talk_patterns:
            elements = soup.find_all(text=lambda text: text and pattern in text)
            if elements:
                print(f"   Patrón '{pattern}': {len(elements)} coincidencias")
                # Mostrar el contexto HTML de las primeras coincidencias
                for elem in elements[:2]:
                    parent = elem.parent
                    if parent and parent.name == 'a':
                        href = parent.get('href', 'N/A')
                        print(f"     Enlace: {href}")
        
    except Exception as e:
        print(f"❌ Error al procesar la URL: {e}")

if __name__ == "__main__":
    # URL de prueba en español (la que viste en la captura)
    test_url = "https://www.churchofjesuschrist.org/study/general-conference/2005/10?lang=spa"
    
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    
    test_talk_extraction(test_url)
