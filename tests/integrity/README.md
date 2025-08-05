# Tests de Integridad para Fases 1 y 2

## 🛡️ Propósito

Los tests de integridad están diseñados para **proteger la funcionalidad crítica de las Fases 1 y 2** mientras se desarrolla la Fase 3. Estos tests garantizan que los cambios futuros no rompan las funcionalidades ya implementadas.

## 📊 Estado Actual: ✅ **30/30 TESTS PASANDO**

### Resumen Ejecutivo
- **Tests Críticos**: 12/12 ✅ - Funcionalidad esencial protegida
- **Tests Generales**: 18/18 ✅ - Integridad completa verificada
- **Cobertura**: 100% de APIs principales y flujos críticos

## 🎯 Categorías de Tests

### 1. Tests Críticos (`@pytest.mark.critical`)
Estos tests **NUNCA deben fallar** y protegen la funcionalidad más esencial:

#### **Fase 1 Crítica (3 tests)**
- ✅ `test_url_collection_basic_workflow` - Workflow principal de recolección
- ✅ `test_database_deduplication_critical` - Deduplicación de URLs
- ✅ `test_configuration_loading_critical` - Carga de configuración

#### **Fase 2 Crítica (3 tests)**
- ✅ `test_talk_extraction_basic_workflow` - Workflow principal de extracción
- ✅ `test_conference_processing_state_critical` - Estado de procesamiento
- ✅ `test_url_validation_security_critical` - Validación de seguridad

#### **Integridad de Datos Crítica (3 tests)**
- ✅ `test_database_connection_resilience` - Resistencia de conexiones
- ✅ `test_data_consistency_under_stress` - Consistencia bajo presión
- ✅ `test_sql_injection_protection` - Protección contra SQL injection

#### **API Principal Crítica (3 tests)**
- ✅ `test_url_collector_api_contract` - Contrato API URLCollector
- ✅ `test_talk_extractor_api_contract` - Contrato API TalkURLExtractor
- ✅ `test_database_manager_api_contract` - Contrato API DatabaseManager

### 2. Tests de Integridad Generales (`@pytest.mark.integrity`)
Protegen funcionalidades específicas y flujos de datos:

#### **Integridad Fase 1 (5 tests)**
- ✅ Inicialización de URLCollector
- ✅ Estructura de base de datos
- ✅ Almacenamiento de URLs de conferencias
- ✅ Integridad de configuración
- ✅ Compatibilidad de API

#### **Integridad Fase 2 (6 tests)**
- ✅ Inicialización de TalkURLExtractor
- ✅ Estructura de base de datos Fase 2
- ✅ Almacenamiento de URLs de talks
- ✅ Estado de procesamiento de conferencias
- ✅ Validación de URLs
- ✅ Compatibilidad de API de extracción

#### **Integridad Entre Fases (4 tests)**
- ✅ Flujo de datos Fase 1 → Fase 2
- ✅ Consistencia de base de datos entre fases
- ✅ Sistema de logging
- ✅ Gestión de sesiones HTTP

#### **Integridad de Base de Datos (3 tests)**
- ✅ Integridad de conexiones
- ✅ Integridad transaccional
- ✅ Integridad de esquema

## 🚨 Funcionalidades Protegidas

### **Fase 1 - Recolección de URLs**
- **URLCollector.collect_all_urls()** - Método principal que nunca debe cambiar signature
- **Deduplicación automática** - URLs duplicadas nunca deben almacenarse
- **Configuración** - Carga de URLs base, selectores CSS, configuración DB
- **Almacenamiento** - URLs deben persistir correctamente en SQLite

### **Fase 2 - Extracción de Talk URLs**
- **TalkURLExtractor.extract_all_talk_urls()** - API principal protegida
- **Estado de procesamiento** - Conferencias procesadas vs. no procesadas
- **Validación de URLs** - Protección contra URLs maliciosas
- **Flujo de datos** - Fase 2 debe acceder a datos de Fase 1

### **Base de Datos**
- **Esquema SQLite** - Tablas: `conference_urls`, `talk_urls`, `processing_log`
- **Constraints UNIQUE** - Prevención de duplicados
- **Transacciones** - Consistencia de datos
- **Seguridad** - Protección contra SQL injection

### **Configuración y APIs**
- **ConfigManager** - Métodos get_base_url(), get_db_path(), etc.
- **DatabaseManager** - Métodos store_*(), get_*(), mark_*()
- **Logging** - Sistema consistente entre fases
- **Sessions HTTP** - User-Agent y configuración de requests

## 🔧 Comandos de Ejecución

### Tests Críticos (Debe ejecutarse antes de cada commit)
```bash
# Solo tests críticos (12 tests)
python -m pytest tests/integrity/ -m critical -v

# Tests críticos con tiempo límite
python -m pytest tests/integrity/ -m critical --maxfail=1 -v
```

### Tests Completos de Integridad
```bash
# Todos los tests de integridad (30 tests)
python -m pytest tests/integrity/ -v

# Con información de cobertura
python -m pytest tests/integrity/ --cov=src -v

# Solo verificar que no fallan (rápido)
python -m pytest tests/integrity/ --tb=no -q
```

### Tests por Fase
```bash
# Solo Fase 1
python -m pytest tests/integrity/ -k "Phase1" -v

# Solo Fase 2  
python -m pytest tests/integrity/ -k "Phase2" -v

# Solo tests de base de datos
python -m pytest tests/integrity/ -k "Database" -v
```

## 🔒 Reglas de Desarrollo para Fase 3

### **Regla 1: Tests Críticos Obligatorios**
- Los 12 tests críticos **DEBEN pasar siempre**
- Ejecutar antes de cada commit: `python -m pytest tests/integrity/ -m critical`
- Si un test crítico falla, **STOP** - no continuar hasta arreglar

### **Regla 2: API Contracts Inmutables**
- Las signatures de estos métodos **NO PUEDEN CAMBIAR**:
  - `URLCollector.collect_all_urls(languages) -> Dict[str, List[str]]`
  - `TalkURLExtractor.extract_all_talk_urls(languages) -> Dict[str, int]`
  - `DatabaseManager.store_conference_urls(language, urls)`
  - `DatabaseManager.get_conference_urls(language) -> List[str]`

### **Regla 3: Esquema de Base de Datos Protegido**
- Las tablas `conference_urls`, `talk_urls`, `processing_log` no pueden modificarse
- Constraints UNIQUE deben mantenerse
- Nuevas tablas para Fase 3 son OK, modificar existentes NO

### **Regla 4: Configuración Backward Compatible**
- Nuevas configuraciones OK, cambiar existentes requiere migración
- URLs base, selectores CSS, configuración DB deben funcionar

### **Regla 5: Flujo de Datos Protegido**
- Fase 3 puede **leer** datos de Fases 1 y 2
- Fase 3 **NO PUEDE** modificar datos de Fases 1 y 2
- Estado de procesamiento de conferencias debe respetarse

## 📈 Monitoreo Continuo

### **Durante Desarrollo de Fase 3**
```bash
# Ejecutar cada hora durante desarrollo activo
python -m pytest tests/integrity/ -m critical --tb=line

# Ejecutar diariamente
python -m pytest tests/integrity/ -v

# Antes de merge/deploy
python -m pytest tests/integrity/ tests/unit/ -v
```

### **Indicadores de Alerta**
- ❌ **Cualquier test crítico falla** → STOP, arreglar inmediatamente
- ⚠️ **Test de integridad falla** → Investigar impacto, posible regresión
- 🔍 **Tiempo de ejecución aumenta >50%** → Revisar eficiencia

## 🎯 Beneficios del Sistema

### **Para Desarrollo**
- **Confianza** para refactorizar código existente
- **Detección temprana** de regresiones
- **Documentación viva** de APIs y comportamientos esperados

### **Para Mantenimiento**
- **Garantía** de que Fases 1 y 2 siguen funcionando
- **Protección** contra cambios accidentales
- **Validación** de que datos históricos siguen siendo accesibles

### **Para Calidad**
- **Estabilidad** del sistema durante expansión
- **Consistencia** de comportamiento
- **Seguridad** contra vulnerabilidades conocidas

---

**Estado**: ✅ **SISTEMA DE INTEGRIDAD COMPLETAMENTE OPERATIVO**  
**Última Verificación**: 5 de agosto de 2025  
**Tests Pasando**: 30/30 (100%)
