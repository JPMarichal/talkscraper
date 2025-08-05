#!/usr/bin/env python3
"""
Script para corregir URLs de conferencias en español que tienen parámetro lang=eng incorrecto.
"""

import sqlite3

def fix_spanish_urls():
    """Corregir URLs de conferencias en español."""
    
    conn = sqlite3.connect('talkscraper_state.db')
    cursor = conn.cursor()
    
    # Buscar URLs marcadas como español pero con parámetro lang=eng
    cursor.execute('SELECT url FROM conference_urls WHERE language = "spa" AND url LIKE "%lang=eng"')
    incorrect_urls = cursor.fetchall()
    
    print(f'🔍 URLs de conferencias españolas con parámetro incorrecto: {len(incorrect_urls)}')
    
    if not incorrect_urls:
        print('✅ No se encontraron URLs con parámetros incorrectos')
        conn.close()
        return
    
    print('\n📋 URLs a corregir:')
    corrections = []
    for i, (url,) in enumerate(incorrect_urls[:10], 1):
        old_url = url
        new_url = url.replace('?lang=eng', '?lang=spa')
        corrections.append((old_url, new_url))
        print(f'{i:2d}. {old_url}')
        print(f'    -> {new_url}')
    
    if len(incorrect_urls) > 10:
        print(f'    ... y {len(incorrect_urls) - 10} más')
    
    # Confirmar antes de proceder
    response = input(f'\n¿Corregir {len(incorrect_urls)} URLs? (s/N): ')
    
    if response.lower() in ['s', 'si', 'sí', 'y', 'yes']:
        print('\n🔧 Corrigiendo URLs...')
        
        corrected = 0
        for old_url, new_url in corrections:
            try:
                cursor.execute('UPDATE conference_urls SET url = ? WHERE url = ?', (new_url, old_url))
                corrected += 1
            except Exception as e:
                print(f'❌ Error corrigiendo {old_url}: {e}')
        
        # Corregir las restantes si hay más de 10
        if len(incorrect_urls) > 10:
            for (url,) in incorrect_urls[10:]:
                old_url = url
                new_url = url.replace('?lang=eng', '?lang=spa')
                try:
                    cursor.execute('UPDATE conference_urls SET url = ? WHERE url = ?', (new_url, old_url))
                    corrected += 1
                except Exception as e:
                    print(f'❌ Error corrigiendo {old_url}: {e}')
        
        conn.commit()
        print(f'✅ {corrected} URLs corregidas exitosamente')
        
        # Verificar resultado
        cursor.execute('SELECT COUNT(*) FROM conference_urls WHERE language = "spa" AND url LIKE "%lang=eng"')
        remaining = cursor.fetchone()[0]
        print(f'📊 URLs españolas con parámetro incorrecto restantes: {remaining}')
        
    else:
        print('❌ Operación cancelada')
    
    conn.close()

if __name__ == "__main__":
    fix_spanish_urls()
