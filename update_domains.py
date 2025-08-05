#!/usr/bin/env python3
"""
Script para actualizar URLs de conference.lds.org a conference.churchofjesuschrist.org
"""

import sqlite3

def update_domains():
    """Actualizar dominios en la base de datos."""
    
    conn = sqlite3.connect('talkscraper_state.db')
    cursor = conn.cursor()
    
    # Buscar URLs con el dominio antiguo
    cursor.execute('SELECT COUNT(*) FROM conference_urls WHERE url LIKE "https://conference.lds.org%"')
    old_count = cursor.fetchone()[0]
    
    print(f'🔍 URLs con dominio antiguo (conference.lds.org): {old_count}')
    
    if old_count == 0:
        print('✅ No hay URLs para actualizar')
        conn.close()
        return
    
    # Mostrar algunos ejemplos
    cursor.execute('SELECT url FROM conference_urls WHERE url LIKE "https://conference.lds.org%" LIMIT 5')
    examples = cursor.fetchall()
    
    print('\n📋 Ejemplos de URLs a actualizar:')
    for i, (url,) in enumerate(examples, 1):
        old_url = url
        new_url = url.replace('https://conference.lds.org', 'https://conference.churchofjesuschrist.org')
        print(f'{i}. {old_url}')
        print(f'   -> {new_url}')
    
    # Confirmar actualización
    response = input(f'\n¿Actualizar {old_count} URLs? (s/N): ')
    
    if response.lower() in ['s', 'si', 'sí', 'y', 'yes']:
        print('\n🔧 Actualizando dominios...')
        
        cursor.execute('''
            UPDATE conference_urls 
            SET url = REPLACE(url, 'https://conference.lds.org', 'https://conference.churchofjesuschrist.org')
            WHERE url LIKE "https://conference.lds.org%"
        ''')
        
        updated = cursor.rowcount
        conn.commit()
        
        print(f'✅ {updated} URLs actualizadas exitosamente')
        
        # Verificar resultado
        cursor.execute('SELECT COUNT(*) FROM conference_urls WHERE url LIKE "https://conference.lds.org%"')
        remaining = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM conference_urls WHERE url LIKE "https://conference.churchofjesuschrist.org%"')
        new_count = cursor.fetchone()[0]
        
        print(f'📊 Resultado:')
        print(f'   URLs con dominio antiguo restantes: {remaining}')
        print(f'   URLs con dominio nuevo: {new_count}')
        
    else:
        print('❌ Operación cancelada')
    
    conn.close()

if __name__ == "__main__":
    update_domains()
