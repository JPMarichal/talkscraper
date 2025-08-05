#!/usr/bin/env python3
"""
Script para limpiar la base de datos de URLs de discursos y resetear el estado de procesamiento.
"""

import sqlite3
from pathlib import Path

def clean_database():
    """Limpiar base de datos de URLs de discursos y resetear procesamiento."""
    
    db_path = Path("talkscraper_state.db")
    
    if not db_path.exists():
        print("❌ No se encontró la base de datos")
        return
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Obtener estadísticas antes de limpiar
        cursor.execute('SELECT COUNT(*) FROM talk_urls')
        talk_count_before = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM conference_urls WHERE processed = 1')
        processed_count_before = cursor.fetchone()[0]
        
        print(f"📊 Estado antes de limpiar:")
        print(f"   - URLs de discursos: {talk_count_before}")
        print(f"   - Conferencias procesadas: {processed_count_before}")
        
        # Eliminar todas las URLs de discursos
        cursor.execute('DELETE FROM talk_urls')
        deleted_talks = cursor.rowcount
        
        # Resetear el estado de procesamiento de conferencias
        cursor.execute('UPDATE conference_urls SET processed = 0')
        updated_conferences = cursor.rowcount
        
        # Confirmar cambios
        conn.commit()
        
        # Verificar resultado
        cursor.execute('SELECT COUNT(*) FROM talk_urls')
        talk_count_after = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM conference_urls WHERE processed = 1')
        processed_count_after = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM conference_urls')
        total_conferences = cursor.fetchone()[0]
        
        print(f"\n✅ Base de datos limpiada exitosamente:")
        print(f"   - {deleted_talks} URLs de discursos eliminadas")
        print(f"   - {updated_conferences} conferencias reseteadas")
        print(f"\n📊 Estado después de limpiar:")
        print(f"   - URLs de discursos: {talk_count_after}")
        print(f"   - Conferencias procesadas: {processed_count_after}")
        print(f"   - Total conferencias disponibles: {total_conferences}")
        
        # Cerrar conexión
        conn.close()
        
    except Exception as e:
        print(f"❌ Error al limpiar la base de datos: {e}")

if __name__ == "__main__":
    clean_database()
