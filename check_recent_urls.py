#!/usr/bin/env python3
"""
Script para verificar URLs más recientes en la base de datos
"""

import sqlite3
from pathlib import Path

def check_recent_urls():
    """Verificar URLs más recientes en la base de datos."""
    
    db_path = Path("talkscraper_state.db")
    
    if not db_path.exists():
        print("❌ No se encontró la base de datos")
        return
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # URLs más recientes no procesadas
        print("📊 URLs más recientes no procesadas (inglés):")
        cursor.execute('''
            SELECT talk_url FROM talk_urls 
            WHERE language = "eng" AND processed = FALSE 
            ORDER BY talk_url DESC LIMIT 10
        ''')
        
        for i, row in enumerate(cursor.fetchall(), 1):
            print(f"   {i}. {row[0]}")
        
        print("\n📊 URLs más recientes no procesadas (español):")
        cursor.execute('''
            SELECT talk_url FROM talk_urls 
            WHERE language = "spa" AND processed = FALSE 
            ORDER BY talk_url DESC LIMIT 10
        ''')
        
        for i, row in enumerate(cursor.fetchall(), 1):
            print(f"   {i}. {row[0]}")
        
        # Estadísticas generales
        cursor.execute('SELECT COUNT(*) FROM talk_urls WHERE language = "eng" AND processed = FALSE')
        eng_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM talk_urls WHERE language = "spa" AND processed = FALSE')
        spa_count = cursor.fetchone()[0]
        
        print(f"\n📈 Estadísticas:")
        print(f"   - URLs inglés no procesadas: {eng_count}")
        print(f"   - URLs español no procesadas: {spa_count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_recent_urls()
