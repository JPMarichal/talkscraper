#!/usr/bin/env python3
"""
Prueba mejorada de extracción de contenido para el discurso de prueba.
"""

import requests
from bs4 import BeautifulSoup
import re
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def extract_improved_content(url):
    """
    Extraer contenido mejorado con formato preservado.
    """
    print(f"🔍 Extrayendo contenido mejorado de: {url}")
    
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Buscar el contenido principal
    content_div = soup.find('div', class_='body-block')
    if not content_div:
        print("❌ No se encontró el div de contenido")
        return None
    
    # Extraer párrafos con formato
    paragraphs = content_div.find_all('p')
    print(f"📄 Párrafos encontrados: {len(paragraphs)}")
    
    formatted_paragraphs = []
    
    for i, p in enumerate(paragraphs):
        p_text = p.get_text(strip=True)
        if len(p_text) < 20:  # Filtrar párrafos muy cortos
            continue
        
        # Comenzar con el párrafo como HTML
        p_html = str(p)
        
        # Buscar referencias a notas y convertirlas en enlaces internos
        note_refs = p.find_all('a', class_='note-ref')
        
        # Crear una copia del párrafo para manipular
        p_copy = BeautifulSoup(str(p), 'html.parser')
        p_elem = p_copy.find('p')
        
        if p_elem:
            # Convertir referencias de notas
            for note_ref in p_elem.find_all('a', class_='note-ref'):
                href = note_ref.get('href', '')
                note_id = href.replace('#', '') if href else note_ref.get_text(strip=True)
                note_text = note_ref.get_text(strip=True)
                
                # Crear un enlace interno a la sección de notas
                new_link = p_copy.new_tag('a', href=f"#note-{note_id}", **{'class': 'note-link'})
                new_link.string = note_text
                note_ref.replace_with(new_link)
            
            # Preservar elementos de énfasis
            for strong in p_elem.find_all(['b']):
                strong.name = 'strong'
            
            for em in p_elem.find_all(['i']):
                em.name = 'em'
            
            formatted_html = str(p_elem)
            
            # Limpiar espacios pero preservar la estructura
            formatted_html = re.sub(r'\s+', ' ', formatted_html)
            formatted_html = formatted_html.strip()
            
            formatted_paragraphs.append(formatted_html)
            
            if i < 5:  # Mostrar los primeros 5 párrafos como ejemplo
                print(f"Párrafo {i+1}: {formatted_html[:200]}...")
    
    print(f"✅ {len(formatted_paragraphs)} párrafos formateados")
    return '\n'.join(formatted_paragraphs)

def generate_improved_html(title, author, calling, content, notes, url):
    """
    Generar HTML mejorado con enlaces a las notas.
    """
    
    # Agregar IDs a las notas para los enlaces
    notes_html = []
    for i, note in enumerate(notes, 1):
        # Extraer el ID de la nota del texto
        note_match = re.match(r'\[note(\d+)\]\s*(.*)', note)
        if note_match:
            note_id = note_match.group(1)
            note_content = note_match.group(2)
        else:
            note_id = str(i)
            note_content = note
        
        notes_html.append(f'<li id="note-{note_id}">{note_content}</li>')
    
    notes_section = '\n        '.join(notes_html)
    
    html_template = f"""<!DOCTYPE html>
<html lang="eng">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - {author}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }}
        .header {{
            text-align: center;
            border-bottom: 2px solid #ccc;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        h1 {{
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        .author {{
            font-size: 1.2em;
            color: #34495e;
            margin-bottom: 5px;
        }}
        .calling {{
            font-style: italic;
            color: #7f8c8d;
            margin-bottom: 10px;
        }}
        .metadata {{
            font-size: 0.9em;
            color: #95a5a6;
        }}
        .content {{
            text-align: justify;
            margin: 30px 0;
        }}
        .content p {{
            margin-bottom: 15px;
        }}
        .note-link {{
            color: #3498db;
            text-decoration: none;
            font-weight: bold;
        }}
        .note-link:hover {{
            text-decoration: underline;
        }}
        .notes {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ccc;
        }}
        .notes h2 {{
            color: #2c3e50;
            margin-bottom: 15x;
        }}
        .notes ol {{
            padding-left: 20px;
        }}
        .notes li {{
            margin-bottom: 8px;
            font-size: 0.9em;
            scroll-margin-top: 20px;
        }}
        .extraction-info {{
            margin-top: 40px;
            padding: 15px;
            background-color: #ecf0f1;
            border-radius: 5px;
            font-size: 0.8em;
            color: #7f8c8d;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <div class="author">{author}</div>
        <div class="calling">{calling}</div>
        <div class="metadata">
            2025-04 | ENG | {len(notes)} notas
        </div>
    </div>
    
    <div class="content">
        {content}
    </div>

    <div class="notes">
        <h2>Notas</h2>
        <ol>
        {notes_section}
        </ol>
    </div>
    
    <div class="extraction-info">
        <strong>Información de extracción:</strong><br>
        URL original: <a href="{url}" target="_blank">{url}</a><br>
        Extraído: Prueba mejorada<br>
        Notas extraídas: {len(notes)}
    </div>
</body>
</html>"""
    
    return html_template

def main():
    """Función principal."""
    url = "https://www.churchofjesuschrist.org/study/general-conference/2025/04/57nelson?lang=eng"
    
    # Extraer contenido mejorado
    content = extract_improved_content(url)
    
    if content:
        # Datos simulados para la prueba
        title = "Confidence in the Presence of God"
        author = "President Russell M. Nelson"
        calling = "President of The Church of Jesus Christ of Latter-day Saints"
        
        # Notas simuladas (normalmente se extraerían con Selenium)
        notes = [
            "[note1] The little stone that the prophet Daniel saw in his dream...",
            "[note2] Doctrine and Covenants 121:45.",
            "[note3] For I will go before your face...",
            # Agregar más notas según sea necesario
        ]
        
        # Generar HTML mejorado
        html_content = generate_improved_html(title, author, calling, content, notes, url)
        
        # Guardar archivo de prueba
        output_file = Path("test_improved_content.html")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Archivo de prueba guardado: {output_file}")
        print("🌐 Abre el archivo en tu navegador para ver el resultado")
    else:
        print("❌ Error al extraer contenido")

if __name__ == "__main__":
    main()
p