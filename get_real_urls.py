#!/usr/bin/env python3
"""
Script para obtener URLs reales de la base de datos
"""
import sqlite3

def get_real_urls():
    conn = sqlite3.connect('talkscraper_state.db')
    cursor = conn.cursor()
    
    # Primero veamos qué hay en la tabla
    cursor.execute('SELECT COUNT(*) FROM talk_urls WHERE language = "eng"')
    count = cursor.fetchone()[0]
    print(f"Total URLs en inglés: {count}")
    
    # Ver algunos ejemplos
    cursor.execute('''
        SELECT talk_url, conference_url 
        FROM talk_urls 
        WHERE language = "eng" 
        ORDER BY talk_url DESC 
        LIMIT 10
    ''')
    
    results = cursor.fetchall()
    
    print("\nPrimeros 10 URLs de discursos:")
    for i, (talk_url, conf_url) in enumerate(results, 1):
        print(f"{i:2d}. {talk_url}")
        print(f"    Conferencia: {conf_url}")
        print()
    
    # También buscar URLs de 2024 específicamente
    cursor.execute('''
        SELECT talk_url, conference_url 
        FROM talk_urls 
        WHERE language = "eng" 
        AND conference_url LIKE '%2024%'
        ORDER BY talk_url 
        LIMIT 5
    ''')
    
    results_2024 = cursor.fetchall()
    
    print("\nURLs de 2024:")
    for i, (talk_url, conf_url) in enumerate(results_2024, 1):
        print(f"{i:2d}. {talk_url}")
        print(f"    Conferencia: {conf_url}")
        print()
    
    conn.close()

if __name__ == "__main__":
    get_real_urls()
