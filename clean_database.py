#!/usr/bin/env python3
"""
Script para limpiar URLs inválidas de la base de datos
"""

import sqlite3
import re
from urllib.parse import urlparse

def is_valid_conference_url(url: str) -> bool:
    """
    Valida si una URL es una conferencia real.
    
    URLs válidas:
    - https://www.churchofjesuschrist.org/study/general-conference/2025/04?lang=eng
    - https://www.churchofjesuschrist.org/study/general-conference/1975/10?lang=spa
    
    URLs inválidas:
    - URLs de décadas: /2010-2019, /1990-1999, etc.
    - URLs de oradores: /speakers/
    - URLs de manuales: /manual/
    - Dominio incorrecto: conference.lds.org
    """
    try:
        parsed = urlparse(url)
        
        # Verificar dominio correcto (ambos dominios son válidos)
        valid_domains = [
            'www.churchofjesuschrist.org',
            'churchofjesuschrist.org', 
            'conference.churchofjesuschrist.org',
            'conference.lds.org'  # Dominio anterior, aún válido por redirección
        ]
        if parsed.netloc not in valid_domains:
            return False
        
        # Verificar que sea una URL de conferencia general
        if '/study/general-conference/' not in parsed.path:
            return False
        
        # Verificar que NO sea una URL de páginas especiales
        if any(x in parsed.path for x in ['/speakers/', '/manual/', '/topics/']):
            return False
        
        # Extraer la parte después de /study/general-conference/
        path_parts = parsed.path.strip('/').split('/')
        
        if len(path_parts) < 4:  # Debe tener al menos: study, general-conference, año, mes
            return False
        
        if path_parts[0] != 'study' or path_parts[1] != 'general-conference':
            return False
        
        year_month = path_parts[2:4]  # [año, mes]
        
        # Verificar formato de año (4 dígitos)
        if not re.match(r'^\d{4}$', year_month[0]):
            return False
        
        # Verificar formato de mes (04 o 10)
        if year_month[1] not in ['04', '10']:
            return False
        
        # Verificar que el año esté en un rango razonable (1971-2030)
        year = int(year_month[0])
        if year < 1971 or year > 2030:
            return False
        
        return True
        
    except Exception:
        return False

def clean_database():
    """Limpia URLs inválidas de la base de datos."""
    db_path = 'talkscraper_state.db'
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Obtener todas las URLs
        cursor.execute('SELECT id, url, language FROM conference_urls')
        all_urls = cursor.fetchall()
        
        print(f'Analizando {len(all_urls)} URLs en la base de datos...')
        
        valid_urls = []
        invalid_urls = []
        
        for url_id, url, language in all_urls:
            if is_valid_conference_url(url):
                valid_urls.append((url_id, url, language))
            else:
                invalid_urls.append((url_id, url, language))
        
        print(f'\n📊 Resultados del análisis:')
        print(f'   ✅ URLs válidas: {len(valid_urls)}')
        print(f'   ❌ URLs inválidas: {len(invalid_urls)}')
        
        if invalid_urls:
            print(f'\n❌ URLs inválidas encontradas:')
            for url_id, url, language in invalid_urls[:10]:  # Mostrar primeras 10
                print(f'   {language.upper()}: {url}')
            if len(invalid_urls) > 10:
                print(f'   ... y {len(invalid_urls) - 10} más')
            
            # Preguntar confirmación antes de borrar
            response = input(f'\n¿Desea eliminar {len(invalid_urls)} URLs inválidas? (s/N): ')
            
            if response.lower() in ['s', 'y', 'yes', 'sí']:
                # Eliminar URLs inválidas
                invalid_ids = [url_id for url_id, _, _ in invalid_urls]
                cursor.executemany('DELETE FROM conference_urls WHERE id = ?', 
                                 [(url_id,) for url_id in invalid_ids])
                
                # También eliminar talk_urls asociadas
                cursor.executemany('DELETE FROM talk_urls WHERE conference_url = ?',
                                 [(url,) for _, url, _ in invalid_urls])
                
                conn.commit()
                
                print(f'✅ {len(invalid_urls)} URLs inválidas eliminadas de la base de datos')
                
                # Verificar estadísticas finales
                cursor.execute('SELECT language, COUNT(*) FROM conference_urls GROUP BY language')
                final_stats = cursor.fetchall()
                
                print(f'\n📊 Estadísticas finales:')
                for lang, count in final_stats:
                    print(f'   {lang.upper()}: {count} conferencias válidas')
            else:
                print('❌ Operación cancelada. No se eliminaron URLs.')
        else:
            print('✅ No se encontraron URLs inválidas.')

if __name__ == '__main__':
    clean_database()
