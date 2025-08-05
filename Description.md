# TalkScraper - Descripción del Proyecto

## Estado Actual del Proyecto ✅ 
**Fase 1 COMPLETADA**: Recolección de URLs de Conferencias
- ✅ **206 conferencias únicas recolectadas**
- ✅ **122 conferencias en inglés** (1971-presente, 53+ años)
- ✅ **84 conferencias en español** (1990-presente, 34+ años)
- ✅ Base de datos SQLite implementada con deduplicación automática
- ✅ Soporte para páginas de décadas y URLs individuales históricas

## Objetivo General
Desarrollar una aplicación de Python que realice el scraping de las conferencias generales de la Iglesia de Jesucristo de los Santos de los Últimos Días en español e inglés.

## Fuente de Datos
- **URL principal**: https://www.churchofjesuschrist.org/study/general-conference?lang=eng
- **Parámetro de idioma**: `lang` puede ser `eng` (inglés) o `spa` (español)

## Estructura de la Página
### Página Principal
La página principal funciona como un archivo de conferencias que contiene:
- Conferencias recientes (2020 en adelante)
- Enlaces a subarchivos organizados por décadas para conferencias anteriores a 2020

### Frecuencia de Conferencias
- Las conferencias generales se realizan **dos veces por año**:
  - **Abril** 
  - **Octubre**

## Funcionalidad del Scraper

### Fase 1: Recolección de URLs ✅ **COMPLETADA**
El scraper implementa exitosamente:
1. ✅ Acceso a la página principal de conferencias
2. ✅ Extracción de todas las URLs de conferencias de la página actual (~24 recientes)
3. ✅ Identificación y acceso a los subarchivos de décadas anteriores:
   - 2010-2019 (20 conferencias)
   - 2000-2009 (20 conferencias) 
   - 1990-1999 (20 conferencias)
   - 1980-1989 (20 conferencias, solo inglés)
4. ✅ Recorrido sistemático de todas las páginas subsidiarias
5. ✅ URLs individuales para años históricos (1971-1979, solo inglés)
6. ✅ **Lista primaria completa compilada**: 206 conferencias únicas sin duplicados

**Resultado**: 
- **122 conferencias en inglés** (1971-presente)
- **84 conferencias en español** (1990-presente)

### Fase 2: Extracción de URLs de Discursos ⏳ **PRÓXIMA**
Una vez obtenida la lista primaria de conferencias, el scraper deberá:
1. Acceder a cada página de conferencia individual (206 páginas)
2. Extraer las URLs de todos los discursos disponibles en cada conferencia
3. Filtrar únicamente los discursos textuales (excluir entradas de solo video)
4. Compilar una **lista completa de discursos** organizada por conferencia
5. **Selector CSS identificado**: `li[data-content-type="general-conference-talk"] a`

### Fase 3: Descarga y Organización de Discursos 🔮 **FUTURO**
El scraper extraerá cada discurso y lo organizará según la siguiente estructura:

#### Estructura de Carpetas
```
/
├── eng/                    # Primer nivel: Idioma
│   ├── 202504/            # Segundo nivel: Fecha (YYYYMM)
│   │   ├── Título del Discurso (Nombre del Orador).html
│   │   └── ...
│   └── 202410/
│       └── ...
└── spa/                    # Primer nivel: Idioma
    ├── 202504/            # Segundo nivel: Fecha (YYYYMM)
    │   ├── Título del Discurso (Nombre del Orador).html
    │   └── ...
    └── 202410/
        └── ...
```

#### Contenido de Archivos HTML
Cada archivo de discurso contendrá:
1. **Título del discurso** (etiqueta H1)
2. **Nombre del discursante**
3. **Posición/cargo del discursante**
4. **Contenido completo del discurso**
5. **Notas** (extracción obligatoria cuando existan)

#### Convenciones de Nomenclatura
- **Nombre de archivo**: Usar nombre común del discursante sin puntos (ejemplo: `Gordon B Hinckley`)
- **Contenido del archivo**: Usar nombre completo con título formal (ejemplo: `Presidente Gordon B. Hinckley`)

#### Criterios de Filtrado
- **Incluir**: Discursos textuales completos
- **Excluir**: Entradas que sean únicamente videos sin contenido textual

## Características Técnicas Avanzadas

### Procesamiento por Lotes
Dado el alto volumen de discursos (aproximadamente **50 discursos por conferencia**), el sistema implementará:
- **Ejecución incremental**: Capacidad de reanudar el procesamiento desde donde se interrumpió la ejecución anterior
- **Procesamiento por lotes**: División del trabajo en lotes manejables para optimizar el rendimiento
- **Persistencia de estado**: Almacenamiento del progreso para permitir continuidad entre ejecuciones

### Control de Errores
- **Manejo robusto de excepciones**: Captura y gestión de errores de red, parsing y E/O
- **Reintentos automáticos**: Estrategia de reintento para conexiones fallidas
- **Logging detallado**: Registro comprehensivo de errores y progreso
- **Recuperación graceful**: Capacidad de continuar el procesamiento después de errores no críticos

### Principios de Desarrollo
El código seguirá los **principios SOLID** y mejores prácticas:
- **Single Responsibility**: Cada clase/módulo con una responsabilidad específica
- **Open/Closed**: Extensible sin modificar código existente
- **Liskov Substitution**: Interfaces consistentes y substituibles
- **Interface Segregation**: Interfaces específicas y cohesivas
- **Dependency Inversion**: Dependencias hacia abstracciones, no implementaciones

### Patrones de Diseño Aplicables
- **Strategy Pattern**: Para diferentes estrategias de scraping según el tipo de página
- **Factory Pattern**: Para creación de scrapers específicos por idioma/período
- **Observer Pattern**: Para notificación de progreso y eventos
- **Command Pattern**: Para operaciones de scraping reutilizables y reversibles

### Requisitos Técnicos
- **Lenguaje**: Python
- **Soporte multiidioma**: Español e Inglés
- **Cobertura temporal**: Desde las conferencias más antiguas disponibles hasta las más recientes

## Especificaciones Técnicas Detalladas

### Tecnologías y Librerías
- **Páginas estáticas**: No requiere JavaScript para contenido principal
- **Notas**: Requieren procesamiento JavaScript - extracción obligatoria
- **Autenticación**: No se requiere login
- **Codificación**: UTF-8 para soporte completo de acentos y diacríticos

#### Librerías Recomendadas
- **Web Scraping**:
  - `requests`: Para realizar peticiones HTTP de manera eficiente
  - `beautifulsoup4`: Para parsing de HTML estático
  - `selenium`: Requerido para extracción de notas con JavaScript
- **Concurrencia**:
  - `asyncio` + `aiohttp`: Para procesamiento asíncrono de múltiples discursos
  - `concurrent.futures`: Para manejo de hilos en operaciones I/O
- **Persistencia y Estado**:
  - `sqlite3` (built-in): Para almacenar estado y progreso del scraping
  - `json` (built-in): Para archivo de configuración
- **Logging y Monitoreo**:
  - `logging` (built-in): Para sistema de logs básico
  - `tqdm`: Para barras de progreso en CLI
- **Manejo de Archivos**:
  - `pathlib` (built-in): Para manejo robusto de rutas de archivos
  - `unicodedata` (built-in): Para normalización de caracteres especiales
- **CLI y Configuración**:
  - `argparse` (built-in): Para interfaz de línea de comandos
  - `configparser` (built-in): Para manejo del archivo de configuración
- **Utilidades**:
  - `urllib.parse` (built-in): Para manipulación de URLs
  - `time` (built-in): Para delays entre requests
  - `re` (built-in): Para expresiones regulares en limpieza de texto

### Configuración de Rendimiento
- **Velocidad de requests**: Sin límite específico, pero aplicar principios razonables
- **Procesamiento concurrente**: 3-5 discursos simultáneos
- **Almacenamiento**: Sin restricciones actuales

### Configuración del Sistema
- **Archivo de configuración**: Requerido para parámetros del sistema
- **Interfaz de línea de comandos**: Necesaria para integración con Task Scheduler de Windows
- **Logging**: Básico y enfocado - inicio/fin de operaciones y errores únicamente

### Manejo de Casos Especiales
- **Títulos duplicados**: Los discursos pueden tener títulos idénticos en diferentes conferencias
- **Extensión de discursos**: Incluir contenido completo sin límite de longitud
- **Caracteres especiales**: Manejo robusto de acentos y diacríticos en nombres de archivos