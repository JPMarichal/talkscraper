#!/usr/bin/env python3
"""
Script para actualizar URLs de conference.churchofjesuschrist.org a www.churchofjesuschrist.org
"""

import sqlite3

def update_to_www_domain():
    """Actualizar todas las URLs para usar www.churchofjesuschrist.org."""
    
    conn = sqlite3.connect('talkscraper_state.db')
    cursor = conn.cursor()
    
    # Buscar URLs con conference.churchofjesuschrist.org
    cursor.execute('SELECT COUNT(*) FROM conference_urls WHERE url LIKE "https://conference.churchofjesuschrist.org%"')
    conference_count = cursor.fetchone()[0]
    
    print(f'🔍 URLs con subdominio "conference": {conference_count}')
    
    if conference_count == 0:
        print('✅ No hay URLs con subdominio "conference" para actualizar')
        conn.close()
        return
    
    # Mostrar algunos ejemplos
    cursor.execute('SELECT url FROM conference_urls WHERE url LIKE "https://conference.churchofjesuschrist.org%" LIMIT 5')
    examples = cursor.fetchall()
    
    print('\n📋 Ejemplos de URLs a actualizar:')
    for i, (url,) in enumerate(examples, 1):
        old_url = url
        new_url = url.replace('https://conference.churchofjesuschrist.org', 'https://www.churchofjesuschrist.org')
        print(f'{i}. {old_url}')
        print(f'   -> {new_url}')
    
    # Confirmar actualización
    response = input(f'\n¿Actualizar {conference_count} URLs al subdominio www? (s/N): ')
    
    if response.lower() in ['s', 'si', 'sí', 'y', 'yes']:
        print('\n🔧 Actualizando subdominios...')
        
        cursor.execute('''
            UPDATE conference_urls 
            SET url = REPLACE(url, 'https://conference.churchofjesuschrist.org', 'https://www.churchofjesuschrist.org')
            WHERE url LIKE "https://conference.churchofjesuschrist.org%"
        ''')
        
        updated = cursor.rowcount
        conn.commit()
        
        print(f'✅ {updated} URLs actualizadas exitosamente')
        
        # Verificar resultado
        cursor.execute('SELECT COUNT(*) FROM conference_urls WHERE url LIKE "https://conference.churchofjesuschrist.org%"')
        remaining_conference = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM conference_urls WHERE url LIKE "https://www.churchofjesuschrist.org%"')
        www_count = cursor.fetchone()[0]
        
        print(f'📊 Resultado:')
        print(f'   URLs con subdominio "conference" restantes: {remaining_conference}')
        print(f'   URLs con subdominio "www": {www_count}')
        
    else:
        print('❌ Operación cancelada')
    
    conn.close()

if __name__ == "__main__":
    update_to_www_domain()
