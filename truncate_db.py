#!/usr/bin/env python3
"""
Script para truncar todas las tablas y empezar desde cero.
"""

import sqlite3

def truncate_all_tables():
    """Truncar todas las tablas de la base de datos."""
    
    conn = sqlite3.connect('talkscraper_state.db')
    cursor = conn.cursor()
    
    # Obtener estadísticas antes de truncar
    cursor.execute('SELECT COUNT(*) FROM conference_urls')
    conference_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM talk_urls')
    talk_count = cursor.fetchone()[0]
    
    print(f'📊 Estado actual de la base de datos:')
    print(f'   URLs de conferencias: {conference_count}')
    print(f'   URLs de discursos: {talk_count}')
    
    # Confirmar truncación
    response = input(f'\n¿Truncar todas las tablas y empezar desde cero? (s/N): ')
    
    if response.lower() in ['s', 'si', 'sí', 'y', 'yes']:
        print('\n🗑️ Truncando tablas...')
        
        # Truncar todas las tablas
        cursor.execute('DELETE FROM talk_urls')
        deleted_talks = cursor.rowcount
        print(f'   ✅ {deleted_talks} URLs de discursos eliminadas')
        
        cursor.execute('DELETE FROM conference_urls')
        deleted_conferences = cursor.rowcount
        print(f'   ✅ {deleted_conferences} URLs de conferencias eliminadas')
        
        # Confirmar cambios
        conn.commit()
        
        # Verificar resultado
        cursor.execute('SELECT COUNT(*) FROM conference_urls')
        remaining_conferences = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM talk_urls')
        remaining_talks = cursor.fetchone()[0]
        
        print(f'\n📊 Base de datos después del truncado:')
        print(f'   URLs de conferencias: {remaining_conferences}')
        print(f'   URLs de discursos: {remaining_talks}')
        print(f'\n✅ Base de datos limpiada. Lista para ejecutar Fase 1 desde cero.')
        
    else:
        print('❌ Operación cancelada')
    
    conn.close()

if __name__ == "__main__":
    truncate_all_tables()
