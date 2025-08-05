#!/usr/bin/env python3
"""
Script para revisar URLs de conferencias en español en la base de datos.
"""

import sqlite3

def check_spanish_urls():
    """Revisar URLs de conferencias en español."""
    
    conn = sqlite3.connect('talkscraper_state.db')
    cursor = conn.cursor()
    
    # Obtener algunas URLs de conferencias en español
    cursor.execute('SELECT url FROM conference_urls WHERE language = "spa" ORDER BY url LIMIT 10')
    spa_urls = cursor.fetchall()
    
    print('📋 Primeras 10 URLs de conferencias en español:')
    for i, (url,) in enumerate(spa_urls, 1):
        print(f'{i:2d}. {url}')
    
    print()
    
    # Verificar si tienen el parámetro lang correcto
    print('🔍 Verificando parámetros de idioma:')
    for i, (url,) in enumerate(spa_urls[:5], 1):
        if '?lang=spa' in url:
            print(f'{i}. ✅ {url} - Parámetro correcto')
        elif '?lang=eng' in url:
            print(f'{i}. ❌ {url} - Parámetro INCORRECTO (debería ser spa)')
        else:
            print(f'{i}. ⚠️  {url} - Sin parámetro de idioma')
    
    # Verificar una URL específica problemática
    print('\n🔍 Verificando URLs específicas que reportaron "No talks found":')
    problem_urls = [
        'https://conference.lds.org/study/general-conference/2020/04?lang=eng',
        'https://www.churchofjesuschrist.org/study/general-conference/2020/04?lang=spa'
    ]
    
    for url in problem_urls:
        cursor.execute('SELECT language FROM conference_urls WHERE url = ?', (url,))
        result = cursor.fetchone()
        if result:
            lang = result[0]
            print(f'   URL: {url}')
            print(f'   Idioma en BD: {lang}')
            if 'lang=eng' in url and lang == 'spa':
                print('   ❌ PROBLEMA: URL tiene lang=eng pero está marcada como spa')
            elif 'lang=spa' in url and lang == 'spa':
                print('   ✅ Correcto: URL y idioma coinciden')
        else:
            print(f'   ⚠️  URL no encontrada en BD: {url}')
    
    conn.close()

if __name__ == "__main__":
    check_spanish_urls()
