#!/usr/bin/env python3
"""Analyze database for Phase 3 test planning."""

import sqlite3
import re
from collections import defaultdict

def analyze_database():
    conn = sqlite3.connect('talkscraper_state.db')
    cursor = conn.cursor()
    
    # Count URLs by language
    cursor.execute('SELECT COUNT(*) FROM talk_urls WHERE language = "eng"')
    eng_count = cursor.fetchone()[0]
    print(f'URLs inglés: {eng_count}')
    
    cursor.execute('SELECT COUNT(*) FROM talk_urls WHERE language = "spa"')
    spa_count = cursor.fetchone()[0]
    print(f'URLs español: {spa_count}')
    
    # Analyze year distribution for English
    print('\n=== Distribución por años (inglés) ===')
    cursor.execute('SELECT talk_url FROM talk_urls WHERE language = "eng"')
    eng_urls = cursor.fetchall()
    
    year_counts_eng = defaultdict(int)
    for (url,) in eng_urls:
        # Extract year from URL like: /general-conference/2024/04/
        match = re.search(r'/general-conference/(\d{4})/', url)
        if match:
            year = match.group(1)
            year_counts_eng[year] += 1
    
    # Show year distribution
    years_eng = sorted(year_counts_eng.keys())
    print(f'Años disponibles (inglés): {years_eng[0]} - {years_eng[-1]}')
    print(f'Total años: {len(years_eng)}')
    
    # Show some example years and their counts
    sample_years = [years_eng[0], years_eng[len(years_eng)//4], years_eng[len(years_eng)//2], 
                   years_eng[3*len(years_eng)//4], years_eng[-1]]
    for year in sample_years:
        print(f'  {year}: {year_counts_eng[year]} discursos')
    
    # Analyze year distribution for Spanish
    print('\n=== Distribución por años (español) ===')
    cursor.execute('SELECT talk_url FROM talk_urls WHERE language = "spa"')
    spa_urls = cursor.fetchall()
    
    year_counts_spa = defaultdict(int)
    for (url,) in spa_urls:
        match = re.search(r'/general-conference/(\d{4})/', url)
        if match:
            year = match.group(1)
            year_counts_spa[year] += 1
    
    years_spa = sorted(year_counts_spa.keys())
    print(f'Años disponibles (español): {years_spa[0]} - {years_spa[-1]}')
    print(f'Total años: {len(years_spa)}')
    
    # Sample URLs for testing
    print('\n=== URLs de muestra ===')
    cursor.execute('SELECT talk_url FROM talk_urls WHERE language = "eng" LIMIT 3')
    sample_eng = cursor.fetchall()
    print('Inglés:')
    for (url,) in sample_eng:
        print(f'  {url}')
    
    cursor.execute('SELECT talk_url FROM talk_urls WHERE language = "spa" LIMIT 3')
    sample_spa = cursor.fetchall()
    print('Español:')
    for (url,) in sample_spa:
        print(f'  {url}')
    
    conn.close()

if __name__ == '__main__':
    analyze_database()
