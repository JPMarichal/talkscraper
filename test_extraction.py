#!/usr/bin/env python3
"""
Script de prueba para verificar la extracción de URLs de discursos.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from scrapers.talk_url_extractor import TalkURLExtractor

def test_single_conference():
    """Probar extracción en una sola conferencia."""
    
    try:
        # Crear extractor
        extractor = TalkURLExtractor()
        
        # URL de prueba (la misma de la captura de pantalla)
        test_url = 'https://www.churchofjesuschrist.org/study/general-conference/2005/10?lang=spa'
        print(f'🔍 Probando extracción de: {test_url}')
        
        # Extraer URLs de discursos
        talk_urls = extractor._extract_conference_talk_urls(test_url)
        print(f'✅ URLs de discursos encontradas: {len(talk_urls)}')
        
        if talk_urls:
            print('\nPrimeros 10 discursos encontrados:')
            for i, url in enumerate(talk_urls[:10]):
                print(f'{i+1:2d}. {url}')
        else:
            print('❌ No se encontraron URLs de discursos')
            
    except Exception as e:
        print(f'❌ Error durante la prueba: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_single_conference()
