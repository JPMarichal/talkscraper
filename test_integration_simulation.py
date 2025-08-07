#!/usr/bin/env python3
"""
Test directo del test de integración corregido.
"""

import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def run_integration_test():
    """Simula el test de integración sin usar pytest framework."""
    try:
        # Import necesarios
        import responses
        from core.url_collector import URLCollector
        from utils.config_manager import ConfigManager
        import tempfile
        import configparser
        
        print("🔍 Ejecutando simulación de test de integración...")
        
        # Crear configuración temporal
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            config = configparser.ConfigParser()
            
            # Default section
            config.set('DEFAULT', 'base_url_eng', 'https://test.example.com/eng')
            config.set('DEFAULT', 'base_url_spa', 'https://test.example.com/spa')
            config.set('DEFAULT', 'eng_dir', 'conf/eng')
            config.set('DEFAULT', 'spa_dir', 'conf/spa')
            config.set('DEFAULT', 'output_dir', 'conf')
            config.set('DEFAULT', 'db_file', 'test_db.sqlite')
            config.set('DEFAULT', 'concurrent_downloads', '3')
            config.set('DEFAULT', 'request_delay', '0.1')
            config.set('DEFAULT', 'log_level', 'INFO')
            config.set('DEFAULT', 'log_file', 'logs/test.log')
            
            # Scraping section
            config.add_section('SCRAPING')
            config.set('SCRAPING', 'user_agent', 'Test-Agent/1.0')
            config.set('SCRAPING', 'conference_link_selector', 'a.test-conference')
            config.set('SCRAPING', 'talk_link_selector', 'a.test-talk')
            config.set('SCRAPING', 'decade_link_selector', 'a.test-decade')
            
            config.write(f)
            test_config_file = f.name
        
        # HTML de ejemplo para mocks
        sample_html = '''
        <!DOCTYPE html>
        <html>
        <head><title>General Conference</title></head>
        <body>
            <div class="conferences">
                <a class="test-conference" href="/study/general-conference/2024/04?lang=eng">April 2024</a>
                <a class="test-conference" href="/study/general-conference/2024/10?lang=eng">October 2024</a>
            </div>
        </body>
        </html>
        '''
        
        # Configurar mocks
        with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
            # Mock main pages
            rsps.add(responses.GET, 'https://test.example.com/eng', body=sample_html, status=200)
            rsps.add(responses.GET, 'https://test.example.com/spa', body=sample_html, status=200)
            
            # Mock decade pages
            for lang in ['eng', 'spa']:
                decade_pages = [
                    f'https://test.example.com/study/general-conference/20102019?lang={lang}',
                    f'https://test.example.com/study/general-conference/20002009?lang={lang}',
                    f'https://test.example.com/study/general-conference/19901999?lang={lang}',
                    f'https://test.example.com/study/general-conference/19801989?lang={lang}'
                ]
                
                for page_url in decade_pages:
                    rsps.add(responses.GET, page_url, body=sample_html, status=200)
            
            # Mock individual year pages
            for lang in ['eng', 'spa']:
                for year in range(1971, 1980):
                    for session in ['04', '10']:
                        year_url = f'https://test.example.com/study/general-conference/{year}/{session}?lang={lang}'
                        rsps.add(responses.GET, year_url, body=sample_html, status=200)
            
            # Ejecutar el test
            collector = URLCollector(test_config_file)
            
            print("📡 Ejecutando collect_all_urls...")
            results = collector.collect_all_urls(['eng', 'spa'])
            
            # Verificaciones
            assert 'eng' in results, "❌ 'eng' no encontrado en resultados"
            assert 'spa' in results, "❌ 'spa' no encontrado en resultados"
            assert len(results['eng']) > 0, "❌ No hay URLs para 'eng'"
            assert len(results['spa']) > 0, "❌ No hay URLs para 'spa'"
            
            print(f"✅ URLs encontradas para ENG: {len(results['eng'])}")
            print(f"✅ URLs encontradas para SPA: {len(results['spa'])}")
            
            # Cleanup
            os.unlink(test_config_file)
            
            print("✅ Test de integración simulado PASÓ")
            return True
        
    except Exception as e:
        print(f"❌ Test de integración simulado FALLÓ: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Ejecutar el test de integración simulado."""
    print("=== TEST DE INTEGRACIÓN SIMULADO ===\n")
    
    # Check if required packages are available
    try:
        import responses
        print("✅ 'responses' package available")
    except ImportError:
        print("❌ 'responses' package not available - installing...")
        import subprocess
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'responses'])
        import responses
    
    success = run_integration_test()
    
    print(f"\n{'='*50}")
    if success:
        print("🎉 TEST DE INTEGRACIÓN SIMULADO EXITOSO")
        print("✅ Los mocks están funcionando correctamente")
        print("💡 Los tests de pytest deberían funcionar ahora")
    else:
        print("⚠️ TEST DE INTEGRACIÓN SIMULADO FALLÓ")
        print("🔧 Se necesitan más correcciones")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
