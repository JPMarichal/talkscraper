#!/usr/bin/env python3
"""
Script de prueba directo para el selector actualizado.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from scrapers.talk_url_extractor import TalkURLExtractor

def test_new_selector():
    """Probar extracción con el selector actualizado."""
    
    try:
        # Crear extractor
        extractor = TalkURLExtractor()
        
        # URLs de prueba - con dominios actualizados
        test_urls = [
            'https://conference.churchofjesuschrist.org/study/general-conference/2022/10?lang=spa',
            'https://www.churchofjesuschrist.org/study/general-conference/2005/10?lang=spa',
            'https://conference.churchofjesuschrist.org/study/general-conference/2024/04?lang=spa'
        ]
        
        for test_url in test_urls:
            print(f'\n🔍 Probando: {test_url}')
            
            # Extraer URLs de discursos
            talk_urls = extractor._extract_conference_talk_urls(test_url)
            print(f'✅ URLs encontradas: {len(talk_urls)}')
            
            if talk_urls:
                print('Primeros 5 discursos:')
                for i, url in enumerate(talk_urls[:5]):
                    print(f'  {i+1}. {url}')
            else:
                print('❌ No se encontraron discursos')
                
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_new_selector()
