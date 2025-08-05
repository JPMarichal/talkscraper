#!/usr/bin/env python3
"""
Script para analizar la estructura HTML de páginas de conferencias más recientes.
"""

import requests
from bs4 import BeautifulSoup
import sys

def analyze_page_structure(url):
    """Analizar estructura HTML para encontrar enlaces de discursos."""
    
    print(f"🔍 Analizando estructura de: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print(f"📄 Página cargada. Tamaño: {len(response.content)} bytes")
        
        # Buscar elementos con las clases mencionadas en los selectores JS
        css_classes_to_test = [
            '.sc-omeqik-7',
            '.iwWCCo', 
            '.sc-omeqik-2',
            '.eHGbnh',
            'li ul li a',
            'nav ul li a',
            'h4 p',
            'div.sc-omeqik-7',
            'div.iwWCCo'
        ]
        
        for i, css_class in enumerate(css_classes_to_test, 1):
            try:
                elements = soup.select(css_class)
                print(f"\n{i}. Selector '{css_class}': {len(elements)} elementos")
                
                if elements and css_class in ['li ul li a', 'nav ul li a']:
                    print("   Primeros 3 elementos:")
                    for j, elem in enumerate(elements[:3]):
                        href = elem.get('href', 'N/A')
                        text = elem.get_text(strip=True)[:60]
                        print(f"     {j+1}. href: {href}")
                        print(f"        texto: {text}")
                        if '/study/general-conference/' in str(href):
                            print(f"        ✅ Contiene enlace de conferencia")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # Buscar estructura de navegación
        print(f"\n🧭 Analizando estructura de navegación:")
        nav_elements = soup.select('nav')
        print(f"   Elementos <nav>: {len(nav_elements)}")
        
        for i, nav in enumerate(nav_elements[:2]):
            links = nav.select('a')
            print(f"   Nav {i+1}: {len(links)} enlaces")
            
            # Buscar enlaces que contengan referencias a discursos
            conference_links = [link for link in links if link.get('href') and '/study/general-conference/' in link.get('href')]
            
            if conference_links:
                print(f"   Enlaces de conferencia en nav {i+1}: {len(conference_links)}")
                for j, link in enumerate(conference_links[:5]):
                    href = link.get('href')
                    text = link.get_text(strip=True)[:50]
                    print(f"     {j+1}. {href}")
                    print(f"        {text}")
                    
                    # Verificar si es enlace individual de discurso
                    parts = href.split('/')
                    if len(parts) >= 6 and parts[4] not in ['', 'saturday-morning-session', 'saturday-afternoon-session', 'sunday-morning-session', 'sunday-afternoon-session']:
                        print(f"        ✅ Parece discurso individual")
                    else:
                        print(f"        ⚠️  Parece sesión o conferencia")
        
        # Buscar listas específicas
        print(f"\n📋 Analizando listas:")
        ul_elements = soup.select('ul')
        print(f"   Total elementos <ul>: {len(ul_elements)}")
        
        # Buscar ul que contengan enlaces de conferencia
        for i, ul in enumerate(ul_elements):
            links = ul.select('a[href*="/study/general-conference/"]')
            if len(links) > 5:  # Solo mostrar ul con varios enlaces
                print(f"\n   UL {i}: {len(links)} enlaces de conferencia")
                for j, link in enumerate(links[:3]):
                    href = link.get('href')
                    text = link.get_text(strip=True)[:50]
                    print(f"     {j+1}. {href} - {text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_url = "https://conference.lds.org/study/general-conference/2022/10?lang=spa"
    
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    
    analyze_page_structure(test_url)
