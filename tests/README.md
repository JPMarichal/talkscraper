# TalkScraper Testing Framework

Este directorio contiene el framework de testing completo para TalkScraper, implementado siguiendo las mejores prácticas de testing con pytest.

## 🧪 Estructura de Testing

```
tests/
├── __init__.py                 # Inicialización del paquete
├── conftest.py                # Configuración global y fixtures
├── unit/                      # Tests unitarios
│   ├── __init__.py
│   ├── test_config_manager.py     # Tests para ConfigManager
│   ├── test_database_manager.py   # Tests para DatabaseManager
│   └── test_phase3_planning.py    # Tests de planificación Fase 3
├── integration/               # Tests de integración
│   ├── __init__.py
│   └── test_url_collection_integration.py
├── fixtures/                  # Fixtures específicos (futuro)
└── data/                     # Datos de prueba
    ├── sample_talk_full.html      # Discurso completo de ejemplo
    ├── sample_main_page.html      # Página principal de ejemplo
    └── sample_conference_page.html # Página de conferencia de ejemplo
```

## 🚀 Ejecutando Tests

### Opción 1: Script de Testing (Recomendado)
```bash
# Ejecutar todos los tests
python run_tests.py --type all

# Solo tests unitarios
python run_tests.py --type unit

# Solo tests de integración
python run_tests.py --type integration

# Tests rápidos (sin selenium ni lentos)
python run_tests.py --type fast

# Tests con cobertura de código
python run_tests.py --type coverage --html-report

# Tests con salida detallada
python run_tests.py --type all --verbose
```

### Opción 2: Pytest Directo
```bash
# Instalar dependencias de testing
pip install -r requirements.txt

# Ejecutar todos los tests
pytest

# Solo tests unitarios
pytest tests/unit/ -m unit

# Solo tests de integración
pytest tests/integration/ -m integration

# Tests con cobertura
pytest --cov=src --cov-report=html

# Tests con marcadores específicos
pytest -m "not slow and not selenium"
pytest -m "database"
pytest -m "network"
```

## 🏷️ Marcadores de Testing

Los tests están organizados usando marcadores de pytest:

- `@pytest.mark.unit` - Tests unitarios
- `@pytest.mark.integration` - Tests de integración
- `@pytest.mark.slow` - Tests que tardan > 30 segundos
- `@pytest.mark.network` - Tests que requieren internet
- `@pytest.mark.database` - Tests que usan base de datos
- `@pytest.mark.selenium` - Tests que usan Selenium

## 🔧 Fixtures Disponibles

### Configuración
- `test_config_dict` - Diccionario de configuración de prueba
- `test_config_file` - Archivo de configuración temporal
- `config_manager` - Instancia de ConfigManager para testing

### Base de Datos
- `test_db_path` - Ruta a base de datos temporal
- `database_manager` - Instancia de DatabaseManager para testing
- `populated_database` - Base de datos con datos de prueba

### HTTP y Mocking
- `mock_requests` - Mock para requests HTTP usando responses
- `sample_html_*` - Contenido HTML de ejemplo para diferentes páginas

### Utilidades
- `temp_dir` - Directorio temporal para tests
- `test_logger` - Logger configurado para testing

## 📊 Cobertura de Código

El framework está configurado para generar reportes de cobertura:

```bash
# Generar reporte de cobertura HTML
python run_tests.py --type coverage --html-report

# Ver reporte en navegador
# Windows
start htmlcov/index.html

# macOS/Linux
open htmlcov/index.html
```

Meta de cobertura: **80%** mínimo

## 🎯 Tests para Fase 3

Los tests de planificación para la Fase 3 están en `test_phase3_planning.py` e incluyen:

### ContentExtractor (Futuro)
- ✅ Planificación de extracción de metadatos
- ✅ Planificación de limpieza de contenido
- ✅ Planificación de extracción de notas

### TalkParser (Futuro)
- ✅ Planificación de parsing de HTML
- ✅ Planificación de sanitización de contenido
- ✅ Planificación de extracción de elementos específicos

### FileOrganizer (Futuro)
- ✅ Planificación de organización de archivos
- ✅ Planificación de naming conventions
- ✅ Planificación de manejo de duplicados

### Selenium Integration (Futuro)
- ✅ Planificación de setup de WebDriver
- ✅ Planificación de extracción de notas JavaScript
- ✅ Planificación de manejo de elementos dinámicos

## 🛠️ Configuración de Desarrollo

### IDE Setup (VS Code)
```json
{
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "tests",
        "--tb=short"
    ],
    "python.testing.autoTestDiscoverOnSaveEnabled": true
}
```

### Pre-commit Hooks (Futuro)
```yaml
# .pre-commit-config.yaml
repos:
-   repo: local
    hooks:
    -   id: pytest-check
        name: pytest-check
        entry: python run_tests.py --type fast
        language: system
        pass_filenames: false
        always_run: true
```

## 📝 Escribiendo Nuevos Tests

### Estructura Básica
```python
import pytest
from utils.my_module import MyClass

class TestMyClass:
    """Test suite for MyClass."""
    
    @pytest.mark.unit
    def test_basic_functionality(self):
        """Test basic functionality."""
        instance = MyClass()
        result = instance.do_something()
        assert result == expected_value
        
    @pytest.mark.integration
    @pytest.mark.database
    def test_database_integration(self, database_manager):
        """Test database integration."""
        # Test implementation
        pass
```

### Mejores Prácticas
1. **Naming**: `test_` prefix, descriptive names
2. **Docstrings**: Describe what the test does
3. **Markers**: Use appropriate pytest markers
4. **Fixtures**: Use fixtures for setup/teardown
5. **Assertions**: Clear, specific assertions
6. **Mock**: Mock external dependencies
7. **Data**: Use test data files when appropriate

## 🚦 Estados de Testing

### ✅ Implementado
- [x] Configuración de pytest
- [x] Fixtures básicos
- [x] Tests unitarios para utilidades existentes
- [x] Tests de integración básicos
- [x] Datos de prueba de ejemplo
- [x] Cobertura de código
- [x] Script de ejecución de tests

### ⏳ En Progreso (Fase 3)
- [ ] Tests para ContentExtractor
- [ ] Tests para TalkParser
- [ ] Tests para FileOrganizer
- [ ] Tests de Selenium
- [ ] Tests de performance

### 🔮 Futuro
- [ ] Tests E2E completos
- [ ] Tests de carga
- [ ] Tests de regression
- [ ] CI/CD integration

## 🤝 Contribuyendo

Para agregar nuevos tests:

1. Identifica el tipo de test (unit/integration)
2. Usa los fixtures apropiados
3. Agrega marcadores pytest apropiados
4. Ejecuta tests antes de commit: `python run_tests.py --type fast`
5. Verifica cobertura: `python run_tests.py --type coverage`

---

**Framework implementado para Fase 3** 🎯  
**Listo para desarrollo basado en pruebas** ✅
