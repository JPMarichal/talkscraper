#!/usr/bin/env python3
"""
Test de extracción de contenido mejorado para un solo discurso.
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from scrapers.talk_content_extractor import TalkContentExtractor

def test_single_talk():
    """Test extraction of a single talk with improved formatting."""
    
    # URL del discurso de prueba
    url = "https://www.churchofjesuschrist.org/study/general-conference/2025/04/57nelson?lang=eng"
    
    print(f"🔍 Probando extracción mejorada para: {url}")
    
    # Crear extractor
    extractor = TalkContentExtractor("config.ini")
    
    # Extraer contenido completo
    talk_data = extractor.extract_complete_talk(url)
    
    if talk_data:
        print(f"✅ Extracción exitosa:")
        print(f"   📝 Título: {talk_data.title}")
        print(f"   👤 Autor: {talk_data.author}")
        print(f"   📊 Notas: {talk_data.note_count}")
        print(f"   📄 Contenido: {len(talk_data.content)} caracteres")
        
        # Verificar que el contenido tiene párrafos separados
        if '<p' in talk_data.content:
            paragraph_count = talk_data.content.count('<p')
            print(f"   📖 Párrafos HTML: {paragraph_count}")
        
        # Verificar enlaces a notas
        if 'note-link' in talk_data.content:
            note_link_count = talk_data.content.count('note-link')
            print(f"   🔗 Enlaces a notas: {note_link_count}")
        
        # Verificar elementos de énfasis
        strong_count = talk_data.content.count('<strong>')
        em_count = talk_data.content.count('<em>')
        print(f"   💪 Elementos strong: {strong_count}")
        print(f"   📝 Elementos em: {em_count}")
        
        # Guardar el archivo mejorado
        saved_path = extractor.save_talk_to_file(talk_data)
        if saved_path:
            print(f"   💾 Guardado en: {saved_path}")
            
            # Mostrar una muestra del contenido
            print("\n📖 Muestra del contenido:")
            content_lines = talk_data.content.split('\n')
            for i, line in enumerate(content_lines[:5]):
                print(f"   {i+1}: {line[:100]}...")
        
        print(f"\n🎯 Prueba completada exitosamente!")
        return True
    else:
        print("❌ Error en la extracción")
        return False

if __name__ == "__main__":
    test_single_talk()
