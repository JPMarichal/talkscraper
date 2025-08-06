# Tests de Fase 3 - Extracción de Contenido Básico

## Descripción

Los tests de Fase 3 validan la capacidad de extraer datos básicos de discursos de la Conferencia General de La Iglesia de Jesucristo de los Santos de los Últimos Días. Estos tests son fundamentales para asegurar que podemos obtener información esencial antes de implementar la extracción de notas más avanzada.

## Funcionalidad Probada

### ✅ Extracción de Metadatos Básicos

Cada test valida la extracción de:

1. **Título del discurso**: Nombre completo del discurso
2. **Autor**: Nombre del orador 
3. **Llamamiento/Posición**: Cargo o posición del orador en la Iglesia
4. **Contenido completo**: Texto completo del discurso limpio de HTML
5. **Año y conferencia**: Información temporal del discurso

### 📊 Cobertura de Pruebas

- **20 discursos aleatorios en inglés** de diferentes años (1971-2024)
- **20 discursos aleatorios en español** de diferentes años (1990-2025)
- **Distribución temporal amplia** para validar cambios en estructura de página
- **Tasa de éxito objetivo**: 75% mínimo (actualmente 100%)

## Estructura de Tests

### TestPhase3BasicContentExtraction

```python
test_random_talk_extraction_english()   # 20 discursos aleatorios en inglés
test_random_talk_extraction_spanish()   # 20 discursos aleatorios en español
test_content_extraction_quality()       # Validación de calidad del contenido
```

### TestPhase3CriticalExtraction

```python
test_extraction_handles_network_errors()      # Manejo robusto de errores
test_extraction_validates_data_integrity()    # Integridad de datos extraídos
```

## Comandos de Ejecución

```bash
# Ejecutar todos los tests de Fase 3
python -m pytest tests/integrity/ -m phase3 -v

# Test específico de inglés
python -m pytest tests/integrity/test_phase3_content_extraction.py::TestPhase3BasicContentExtraction::test_random_talk_extraction_english -v -s

# Test específico de español
python -m pytest tests/integrity/test_phase3_content_extraction.py::TestPhase3BasicContentExtraction::test_random_talk_extraction_spanish -v -s

# Tests críticos solamente
python -m pytest tests/integrity/test_phase3_content_extraction.py::TestPhase3CriticalExtraction -v
```

## Validaciones Implementadas

### ✅ Validaciones de Contenido

1. **Título**: Mínimo 5 caracteres, sin HTML
2. **Autor**: Mínimo 3 caracteres, limpieza de prefijos "By/Por"
3. **Contenido**: Mínimo 500 caracteres, limpio de etiquetas HTML
4. **Integridad**: Sin restos de código HTML en texto final

### ✅ Validaciones de Calidad

1. **Contenido espiritual**: Presencia de términos religiosos apropiados
2. **Diversidad temporal**: Cobertura de múltiples años y décadas
3. **Consistencia de idioma**: Validación correcta de idioma por URL
4. **Robustez de red**: Manejo apropiado de errores de conexión

## Datos de Rendimiento

### Última Ejecución Exitosa

**Test en Inglés (20 discursos):**
- ✅ Tasa de éxito: 100% (20/20)
- 📅 Años cubiertos: 18 años diferentes (1971-2024)
- ⏱️ Tiempo de ejecución: ~14 segundos
- 🎯 Autores diversos: Presidentes, Apóstoles, Autoridades Generales

**Test en Español (20 discursos):**
- ✅ Tasa de éxito: 100% (20/20)  
- 📅 Años cubiertos: 17 años diferentes (1990-2025)
- ⏱️ Tiempo de ejecución: ~20 segundos
- 🎯 Autores diversos: Líderes de todas las organizaciones

## Arquitectura del Extractor

### BasicContentExtractor

```python
class BasicContentExtractor:
    def extract_talk_metadata(url: str) -> Optional[TalkMetadata]
    def _extract_title(soup: BeautifulSoup) -> Optional[str]
    def _extract_author(soup: BeautifulSoup) -> Optional[str]  
    def _extract_calling(soup: BeautifulSoup) -> Optional[str]
    def _extract_content(soup: BeautifulSoup) -> Optional[str]
```

### TalkMetadata

```python
@dataclass
class TalkMetadata:
    title: str
    author: str
    calling: str
    content: str
    url: str
    language: str
    year: str
    conference_session: str
```

## Próximos Pasos

### Fase 3 Avanzada

1. **Extracción de notas**: Referencias de escrituras y notas al pie
2. **Mejora de llamamiento**: Extracción más precisa de posiciones
3. **Metadatos adicionales**: Sesión específica, tema del discurso
4. **Optimización**: Cacheo y mejoras de rendimiento

### Integración

1. **Selenium**: Para contenido dinámico y JavaScript
2. **Almacenamiento**: Persistencia de contenido extraído
3. **Organización**: Sistema de archivos estructurado
4. **Procesamiento**: Pipeline de limpieza y formateo

## Criterios de Éxito

- ✅ **Extracción básica funcionando**: 100% completado
- ⏳ **Extracción de notas**: Pendiente de implementación
- ⏳ **Sistema de archivos**: Pendiente de implementación
- ⏳ **Pipeline completo**: Pendiente de integración

Los tests de Fase 3 proporcionan la base sólida necesaria para desarrollar con confianza las funcionalidades avanzadas de extracción de contenido.
