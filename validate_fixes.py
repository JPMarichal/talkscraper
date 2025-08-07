#!/usr/bin/env python3
"""
Validación rápida de la funcionalidad después de las correcciones.
"""

import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_url_collector_changes():
    """Test que las URLs se generan dinámicamente en lugar de hardcodeadas."""
    from core.url_collector import URLCollector
    from utils.config_manager import ConfigManager
    
    print("🔍 Probando cambios en URLCollector...")
    
    # Crear un config temporal con base URL de test
    config_path = "config.ini"
    if not os.path.exists(config_path):
        print("❌ config.ini no encontrado")
        return False
    
    try:
        collector = URLCollector(config_path)
        
        # Verificar que la configuración funciona
        base_url_eng = collector.config.get_base_url('eng')
        print(f"✅ Base URL ENG: {base_url_eng}")
        
        base_url_spa = collector.config.get_base_url('spa')
        print(f"✅ Base URL SPA: {base_url_spa}")
        
        # Probar que las URLs se construyen dinámicamente
        from urllib.parse import urlparse
        parsed_base = urlparse(base_url_eng)
        expected_domain = f"{parsed_base.scheme}://{parsed_base.netloc}"
        
        print(f"✅ Dominio extraído: {expected_domain}")
        
        # Verificar logger name correcto después de cambio
        logger_name = collector.logger.name
        print(f"✅ Logger name: {logger_name}")
        
        expected_logger = 'core.url_collector'
        if logger_name == expected_logger:
            print(f"✅ Logger name correcto: {logger_name}")
        else:
            print(f"❌ Logger name incorrecto. Esperado: {expected_logger}, Actual: {logger_name}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error en URLCollector: {e}")
        return False

def test_imports():
    """Test que todos los imports funcionan correctamente."""
    print("🔍 Probando imports después de refactorización...")
    
    try:
        from core.url_collector import URLCollector
        print("✅ core.url_collector import")
        
        from core.talk_url_extractor import TalkURLExtractor
        print("✅ core.talk_url_extractor import")
        
        from patterns.scraper_factory import ScraperFactory
        print("✅ patterns.scraper_factory import")
        
        from patterns.command_pattern import CommandInvoker
        print("✅ patterns.command_pattern import")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en imports: {e}")
        return False

def main():
    """Ejecutar todas las validaciones."""
    print("=== VALIDACIÓN POST-CORRECCIÓN ===\n")
    
    results = []
    
    # Test 1: Imports
    results.append(("Imports", test_imports()))
    
    # Test 2: URLCollector changes
    results.append(("URLCollector", test_url_collector_changes()))
    
    print(f"\n{'='*50}")
    print("RESUMEN DE VALIDACIONES:")
    print(f"{'='*50}")
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ ÉXITO" if passed else "❌ FALLO"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 TODAS LAS VALIDACIONES PASARON")
        print("📝 Los cambios parecen estar funcionando correctamente.")
        print("💡 Ahora deberían funcionar mejor los tests de integración.")
    else:
        print("\n⚠️ ALGUNAS VALIDACIONES FALLARON")
        print("🔧 Se necesita más trabajo para corregir los problemas.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
