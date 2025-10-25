# TalkScraper 🎤

**TalkScraper** es una aplicación de Python diseñada para extraer sistemáticamente las conferencias generales de la Iglesia de Jesucristo de los Santos de los Últimos Días en español e inglés.

## 🎯 Objetivo

Crear una herramienta robusta que recopile todos los discursos de conferencias generales desde 1971 hasta la actualidad, organizándolos en una estructura jerárquica por idioma y fecha.

## 🏗️ Arquitectura del Proyecto

### Fases de Implementación

1. **Fase 1: Recolección de URLs** ✅ **(COMPLETADA)**
   - ✅ Extracción de URLs de conferencias desde la página principal
   - ✅ Procesamiento de archivos de décadas anteriores (2010-2019, 2000-2009, 1990-1999, 1980-1989)
   - ✅ URLs individuales para años históricos (1971-1979)
   - ✅ Almacenamiento en base de datos SQLite con deduplicación
   - ✅ **Resultado (octubre 2025): 206 conferencias únicas (123 ENG + 83 SPA)**

2. **Fase 2: Extracción de URLs de Discursos** ✅ **(COMPLETADA)**
   - ✅ Obtención de URLs individuales de discursos desde cada conferencia
   - ✅ Filtrado de contenido textual vs. videos
   - ✅ Almacenamiento incremental y marcado de progreso

3. **Fase 3: Extracción de Contenido** 🚧 **(EN PROGRESO)**
   - Extracción de contenido estático (título, autor, llamamiento, cuerpo)
   - Extracción opcional de notas (Selenium, `--skip-notes`)
   - Organización en estructura de carpetas por idioma/fecha
   - Respaldo de metadatos en `talk_metadata`

## 📁 Estructura del Proyecto

```
talkscraper/
├── src/                    # Código fuente
│   ├── scrapers/          # Módulos de scraping
│   │   ├── url_collector.py
│   │   └── __init__.py
│   ├── utils/             # Utilidades
│   │   ├── config_manager.py
│   │   ├── database_manager.py
│   │   ├── logger_setup.py
│   │   └── __init__.py
│   └── __init__.py
├── conf/                  # Directorio de extracción
│   ├── eng/              # Discursos en inglés
│   └── spa/              # Discursos en español
├── logs/                 # Archivos de log
├── tests/                # Tests unitarios (futuro)
├── main.py              # Script principal
├── config_template.ini  # Plantilla de configuración
├── config.ini          # Configuración (generado)
├── requirements.txt     # Dependencias
├── setup.bat           # Script de instalación (Windows)
└── setup.sh            # Script de instalación (Unix/Linux/macOS)
```

## 🚀 Instalación y Configuración

### Opción 1: Instalación Automática (Windows)
```bash
.\setup.bat
```

### Opción 2: Instalación Manual
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate.bat
# Unix/Linux/macOS:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Copiar configuración
copy config_template.ini config.ini  # Windows
cp config_template.ini config.ini    # Unix/Linux/macOS
```

## 📝 Configuración

El archivo `config.ini` contiene todas las configuraciones del sistema:

```ini
[DEFAULT]
base_url_eng = https://www.churchofjesuschrist.org/study/general-conference?lang=eng
base_url_spa = https://www.churchofjesuschrist.org/study/general-conference?lang=spa
concurrent_downloads = 5
request_delay = 1.0

[SCRAPING]
user_agent = Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
selenium_headless = true
conference_link_selector = a.portrait-jkM1
```

## 🔧 Uso

### Recolección de URLs (Fase 1)
```bash
# Recopilar URLs para ambos idiomas
python main.py --phase 1

# Solo inglés
python main.py --phase 1 --languages eng

# Solo español
python main.py --phase 1 --languages spa

# Ver estadísticas
python main.py --stats

# Verbose logging
python main.py --phase 1 --verbose
```

### Ejemplos de Salida
```
=== PHASE 1: URL COLLECTION ===
Languages: eng, spa
Config: config.ini

✅ ENG: 123 conference URLs collected
✅ SPA: 83 conference URLs collected

🎯 Total URLs collected: 206

📊 Database Statistics:
   ENG: 122 total, 0 processed (0.0%)
   SPA: 84 total, 0 processed (0.0%)
```

## 📊 Cobertura Histórica Actual

### URLs Recolectadas por Fuente:

**🇺🇸 Inglés (123 conferencias únicas)**
- Página principal: ~25 URLs (2020-presente)
- Década 2010-2019: 20 URLs
- Década 2000-2009: 20 URLs  
- Década 1990-1999: 20 URLs
- Década 1980-1989: 20 URLs
- URLs individuales 1971-1979: 18 URLs
- **Cobertura: 1971-presente (53+ años)**

**🇪🇸 Español (83 conferencias únicas)**
- Página principal: ~23 URLs (2020-presente)
- Década 2010-2019: 20 URLs
- Década 2000-2009: 20 URLs
- Década 1990-1999: 20 URLs
- (Décadas anteriores no disponibles en español)
- **Cobertura: 1990-presente (34+ años)**

## 🧪 Testing & QA

El proyecto incluye un framework completo de testing basado en pytest y se integra con CI (GitHub Actions) para ejecutar la suite "fast" en cada push/pull request a `main`.

### Ejecutar Tests
```bash
# Instalar dependencias de testing
pip install -r requirements.txt

# Ejecutar suite rápida (sin marcadores slow/selenium)
python run_tests.py --type fast

# Solo tests unitarios
python run_tests.py --type unit

# Solo tests de integración 
python run_tests.py --type integration

# Todos los tests (unitarios + integración + reporte de cobertura)
python run_tests.py --type all

# Tests con cobertura de código
python run_tests.py --type coverage --html-report

# Tests rápidos (sin selenium)
python run_tests.py --type fast
```

### Estructura de Testing
- **Unit Tests**: Tests para componentes individuales (`tests/unit/`)
- **Integration Tests**: Tests para flujos completos (`tests/integration/`)
- **Test Data**: Datos de ejemplo para testing (`tests/data/`)
- **Fixtures**: Configuraciones reutilizables (`tests/conftest.py`)

Ver [tests/README.md](tests/README.md) para más detalles.

## 🛠️ Características Técnicas

### Tecnologías Utilizadas
- **Python 3.8+**
- **requests** + **BeautifulSoup4**: Scraping de páginas estáticas
- **Selenium**: Extracción de notas con JavaScript
- **SQLite**: Persistencia de estado y progreso
- **asyncio**: Procesamiento concurrente
- **tqdm**: Barras de progreso

### Principios de Desarrollo
- **Principios SOLID**
- **Patrones de diseño**: Strategy, Factory, Observer, Command
- **Manejo robusto de errores**
- **Logging detallado**
- **Procesamiento por lotes**
- **Codificación UTF-8**

### Optimizaciones de Rendimiento
- **Procesamiento concurrente**: 3-5 discursos simultáneos
- **Cache en memoria**: Aprovecha 64GB RAM disponibles
- **Reintentos automáticos**: Para conexiones fallidas
- **Ejecución incremental**: Reanuda desde interrupciones

## 📊 Estructura de Datos

### Base de Datos SQLite
```sql
-- URLs de conferencias
conference_urls(id, language, url, discovered_date, processed)

-- URLs de discursos individuales
talk_urls(id, conference_url, talk_url, language, discovered_date, processed)

-- Log de procesamiento
processing_log(id, operation, language, url, status, message, timestamp)
```

### Estructura de Salida (Futuro - Fase 3)
```
conf/
├── eng/
│   ├── 202504/
│   │   ├── As a Little Child (Jeffrey R Holland).html
│   │   └── Spiritually Whole in Him (Camille N Johnson).html
│   └── 202410/
└── spa/
    ├── 202504/
    └── 202410/
```

## 🎯 Selectores CSS Identificados

Basado en el análisis de la estructura HTML:

- **Enlaces de conferencias**: `a.portrait-jkM1`
- **Enlaces de discursos**: `li[data-content-type="general-conference-talk"] a`
- **Enlaces de décadas**: `a[href*="/study/general-conference/"]`

## 📈 Estado Actual

### ✅ Completado (Fase 1)
- [x] Estructura del proyecto
- [x] Sistema de configuración
- [x] Base de datos SQLite
- [x] Logging y monitoreo
- [x] Extracción de URLs principales
- [x] Extracción de URLs de páginas de décadas (2010-2019, 2000-2009, 1990-1999, 1980-1989)
- [x] Extracción de URLs individuales para años históricos (1971-1979)
- [x] Deduplicación automática de URLs
- [x] Interfaz de línea de comandos
- [x] Manejo de errores robusto
- [x] **206 conferencias únicas recolectadas y almacenadas**

### ✅ Fase 2 completada
- [x] Extracción de URLs de discursos individuales desde cada conferencia
- [x] Análisis de estructura HTML de páginas de conferencias
- [x] Implementación del selector CSS para discursos: `li[data-content-type="general-conference-talk"] a`

### 🚧 Fase 3 en progreso
- [x] Extracción de contenido estático con respaldo en DB
- [x] Modo `--skip-notes` para omitir Selenium
- [x] Reintentos por discurso y logging en `processing_log`
- [ ] Extracción de notas vía Selenium
- [ ] Organización completa en carpetas finales
- [ ] Documentación API / reportes finales

## 🤝 Contribución

Este proyecto sigue los principios SOLID y utiliza patrones de diseño bien establecidos. Para contribuir:

1. Fork el repositorio
2. Crea una rama para tu feature
3. Implementa siguiendo los patrones existentes
4. Agrega tests si es necesario
5. Submite un Pull Request

## 📄 Licencia

Este proyecto está desarrollado para uso educativo y de investigación, respetando los términos de uso del sitio web fuente.

---

**Estado**: Fase 3 en progreso 🚧 | **206 conferencias** y **>1.5K URLs de discursos** procesadas📊  
**CI**: Workflow `tests.yml` ejecuta `python run_tests.py --type fast --verbose` en cada push/PR
