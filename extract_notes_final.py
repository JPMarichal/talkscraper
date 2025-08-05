#!/usr/bin/env python3
"""
Versión final de extracción de notas - usando innerHTML de elementos li
"""
import sqlite3
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import time

def extract_talk_content_static(url):
    """Extrae contenido estático del discurso usando requests + BeautifulSoup"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extraer título
    title_element = soup.find('h1')
    title = title_element.get_text(strip=True) if title_element else "Sin título"
    
    # Buscar información del autor
    author_element = (soup.find('p', class_='author-name') or 
                     soup.find('div', class_='byline') or
                     soup.find('p', string=re.compile(r'^(By|Por)\s+')) or
                     soup.find('h2'))
    
    author = ""
    if author_element:
        author = author_element.get_text(strip=True)
        author = re.sub(r'^(By|Por)\s+', '', author)
    else:
        author = "Autor no encontrado"
    
    # Buscar cargo/posición
    position_element = (soup.find('p', class_='author-role') or 
                       soup.find('div', class_='author-role') or
                       soup.find('p', class_='author-title') or 
                       soup.find('div', class_='author-title'))
    position = position_element.get_text(strip=True) if position_element else "Posición no encontrada"
    
    # Extraer contenido principal del discurso
    content_div = soup.find('div', class_='body-block') or soup.find('div', id='main-content')
    if not content_div:
        content_div = soup.find('div', class_='article-content') or soup.find('main')
    
    content = ""
    if content_div:
        for p in content_div.find_all('p'):
            content += p.get_text(strip=True) + "\n\n"
    else:
        content = "Contenido no encontrado"
    
    return {
        'title': title,
        'author': author,
        'position': position,
        'content': content.strip(),
        'url': url
    }

def extract_notes_with_selenium_final(url):
    """Extrae las notas usando innerHTML de elementos li - versión final"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=chrome_options)
    notes = []
    
    try:
        print(f"🌐 Cargando página: {url}")
        driver.get(url)
        
        # Esperar a que la página cargue
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print("✅ Página cargada")
        
        # Buscar y activar el botón "Related Content"
        print("🔍 Activando 'Related Content'...")
        try:
            related_content_selectors = [
                'button[data-testid="related-content"]',
                'button[aria-label*="Related"]',
                'button[title*="Related"]'
            ]
            
            activated = False
            for selector in related_content_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        element = elements[0]
                        if element.is_displayed() and element.is_enabled():
                            driver.execute_script("arguments[0].click();", element)
                            print(f"✅ Activado 'Related Content'")
                            activated = True
                            break
                except Exception:
                    continue
            
            if activated:
                # Esperar a que se cargue el contenido relacionado
                print("⏳ Esperando contenido relacionado...")
                time.sleep(5)
                
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "aside"))
                    )
                    print("✅ Panel aside detectado")
                    time.sleep(3)  # Tiempo adicional para que se carguen las notas
                    
                except Exception as e:
                    print(f"⚠️ No se detectó panel aside: {e}")
            else:
                print("⚠️ No se pudo activar 'Related Content'")
        
        except Exception as e:
            print(f"⚠️ Error al activar Related Content: {e}")
        
        # Extraer notas de elementos li usando innerHTML
        print("🔍 Extrayendo notas de elementos <li>...")
        note_li_elements = driver.find_elements(By.CSS_SELECTOR, 'li[id^="note"]')
        print(f"📝 Elementos <li> encontrados: {len(note_li_elements)}")
        
        for element in note_li_elements:
            note_id = element.get_attribute('id')
            try:
                # Obtener el innerHTML que contiene el contenido completo
                inner_html = driver.execute_script("return arguments[0].innerHTML;", element)
                
                if inner_html and inner_html.strip():
                    # Crear una instancia de BeautifulSoup para limpiar el HTML
                    soup = BeautifulSoup(inner_html, 'html.parser')
                    # Extraer solo el texto limpio
                    clean_text = soup.get_text(strip=True)
                    
                    if clean_text and len(clean_text) > 5:
                        print(f"  ✅ Nota {note_id}: {clean_text[:100]}...")
                        notes.append(f"[{note_id}] {clean_text}")
                    
            except Exception as e:
                print(f"  ❌ Error procesando {note_id}: {e}")
        
        print(f"📝 Total notas extraídas: {len(notes)}")
        
    except Exception as e:
        print(f"❌ Error general: {e}")
    finally:
        driver.quit()
    
    return notes

def main():
    """Función principal para probar la extracción final"""
    print("=== EXTRACCIÓN FINAL DE NOTAS ===")
    
    url = "https://www.churchofjesuschrist.org/study/general-conference/2025/04/13holland?lang=eng"
    
    print(f"🎯 URL de prueba: {url}")
    print("-" * 60)
    
    # Extraer contenido estático
    print("📄 Extrayendo contenido estático...")
    try:
        static_data = extract_talk_content_static(url)
        
        print(f"📋 TÍTULO: {static_data['title']}")
        print(f"👤 AUTOR: {static_data['author']}")
        print(f"🏛️ POSICIÓN: {static_data['position']}")
        print(f"📝 CONTENIDO: {len(static_data['content'])} caracteres")
        print("-" * 60)
        
    except Exception as e:
        print(f"❌ Error al extraer contenido estático: {e}")
        return
    
    # Extraer notas con versión final
    print("🔍 Extrayendo notas (versión final)...")
    try:
        notes = extract_notes_with_selenium_final(url)
        
        if notes:
            print(f"\n✅ NOTAS EXTRAÍDAS EXITOSAMENTE: {len(notes)}")
            print("=" * 60)
            for i, note in enumerate(notes, 1):
                print(f"{i:2}. {note}")
            print("=" * 60)
        else:
            print("❌ No se encontraron notas")
        
    except Exception as e:
        print(f"❌ Error al extraer notas: {e}")
    
    print("\n✅ Prueba final completada")

if __name__ == "__main__":
    main()
