#!/usr/bin/env python3
"""
TalkScraper - Continuación ESTABLE de extracción con recursos limitados

Esta versión está optimizada para sistemas bajo stress:
- Solo 6 hilos concurrentes para reducir carga CPU/memoria
- Configuración Chrome ultra-conservadora
- Timeouts más largos para mayor estabilidad
- Escritura inmediata de archivos para reducir uso de memoria
- Pausas entre lotes para permitir que el sistema respire
"""

import sys
import argparse
import time
import gc
import psutil
from pathlib import Path
from typing import List, Set

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from scrapers.talk_content_extractor import TalkContentExtractor
from utils.config_manager import ConfigManager
from utils.logger_setup import setup_logger


def get_completed_periods() -> Set[str]:
    """Detectar períodos ya completados basándose en estructura de archivos."""
    completed = set()
    conf_dir = Path('conf/eng')
    
    if not conf_dir.exists():
        return completed
    
    for period_dir in conf_dir.iterdir():
        if period_dir.is_dir() and period_dir.name.isdigit() and len(period_dir.name) == 6:
            # Verificar si el período tiene archivos suficientes
            html_files = list(period_dir.glob('*.html'))
            if len(html_files) >= 3:  # Mínimo 3 archivos para considerar completo
                completed.add(period_dir.name)
    
    return completed


def filter_unprocessed_urls(all_urls: List[str], completed_periods: Set[str]) -> List[str]:
    """Filtrar URLs para procesar solo las no completadas."""
    unprocessed = []
    
    for url in all_urls:
        # Extraer período de la URL (YYYYMM)
        try:
            parts = url.split('/')
            for part in parts:
                if 'general-conference' in url:
                    conf_idx = parts.index('general-conference')
                    if conf_idx + 2 < len(parts):
                        year = parts[conf_idx + 1]
                        month = parts[conf_idx + 2]
                        if month == '04':
                            period = year + '04'
                        elif month == '10':
                            period = year + '10'
                        else:
                            period = None
                        
                        if period and period not in completed_periods:
                            unprocessed.append(url)
                        break
        except Exception:
            # Si no podemos determinar el período, incluir la URL
            unprocessed.append(url)
    
    return unprocessed


def check_system_resources():
    """Verificar recursos del sistema y retornar recomendación de pausa."""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        if cpu_percent > 80 or memory.percent > 85:
            return True, f"CPU: {cpu_percent:.1f}%, RAM: {memory.percent:.1f}%"
        return False, f"CPU: {cpu_percent:.1f}%, RAM: {memory.percent:.1f}%"
    except Exception:
        return False, "No se pudo verificar recursos"


def main():
    """Proceso principal de continuación estable."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Continuación ESTABLE de extracción Phase 3')
    parser.add_argument('--batch-size', type=int, default=6,
                       help='Hilos concurrentes (default: 6 - estable)')
    parser.add_argument('--config', default='config.ini',
                       help='Archivo de configuración')
    parser.add_argument('--pause-between-batches', type=int, default=10,
                       help='Pausa entre lotes en segundos (default: 10)')
    
    args = parser.parse_args()
    
    # Setup logger
    config = ConfigManager(args.config)
    log_config = config.get_log_config()
    logger = setup_logger('ContinueExtractionStable', log_config)
    
    logger.info("=" * 70)
    logger.info("CONTINUACIÓN ESTABLE DE EXTRACCIÓN - RECURSOS LIMITADOS")
    logger.info("=" * 70)
    logger.info(f"Hilos concurrentes: {args.batch_size}")
    logger.info(f"Pausa entre lotes: {args.pause_between_batches}s")
    
    try:
        # Verificar recursos del sistema
        needs_pause, resources = check_system_resources()
        logger.info(f"📊 Recursos del sistema: {resources}")
        if needs_pause:
            logger.warning("⚠️  Sistema bajo stress - usando configuración ultra-conservadora")
            args.batch_size = min(args.batch_size, 4)  # Reducir aún más si es necesario
        
        # Detectar períodos completados
        logger.info("📁 Analizando períodos ya procesados...")
        completed_periods = get_completed_periods()
        logger.info(f"📁 Encontrados {len(completed_periods)} períodos ya procesados")
        
        if completed_periods:
            sorted_periods = sorted(completed_periods, reverse=True)
            logger.info(f"   Último período completo: {sorted_periods[0]}")
        
        # Obtener URLs de la base de datos
        logger.info(f"\n📊 Obteniendo URLs completas de la base de datos...")
        extractor = TalkContentExtractor(args.config)
        all_talk_urls = extractor.get_unprocessed_talk_urls('eng', None)
        logger.info(f"📋 URLs totales en base de datos: {len(all_talk_urls)}")
        
        # Filtrar URLs realmente no procesadas
        unprocessed_urls = filter_unprocessed_urls(all_talk_urls, completed_periods)
        logger.info(f"🎯 URLs realmente no procesadas: {len(unprocessed_urls)}")
        
        if not unprocessed_urls:
            logger.info("✅ No hay URLs pendientes por procesar")
            return
        
        # Mostrar rango de procesamiento
        logger.info(f"\n🔍 Rango de URLs a procesar:")
        logger.info(f"   Primera: {unprocessed_urls[0]}")
        logger.info(f"   Última: {unprocessed_urls[-1]}")
        
        # Calcular estimación de tiempo con configuración estable
        estimated_time_per_talk = 8  # Más conservador por la configuración limitada
        total_estimated_minutes = (len(unprocessed_urls) * estimated_time_per_talk) / 60
        
        logger.info(f"\n⚠️  Se van a procesar {len(unprocessed_urls)} discursos restantes.")
        logger.info(f"🕐 Tiempo estimado: {total_estimated_minutes:.1f} minutos (~{total_estimated_minutes/60:.1f} horas)")
        logger.info("💡 Configuración ESTABLE - menor uso de recursos")
        logger.info("🚀 Iniciando procesamiento ESTABLE en 3 segundos...")
        time.sleep(3)
        
        # Procesar en lotes pequeños con pausas
        batch_size = args.batch_size
        total_processed = 0
        total_successful = 0
        total_failed = 0
        start_time = time.time()
        
        logger.info(f"\n🚀 Iniciando extracción estable desde el punto correcto...")
        
        # Procesar en chunks para manejar mejor la memoria
        chunk_size = 50  # Procesar 50 URLs y luego hacer limpieza de memoria
        
        for chunk_start in range(0, len(unprocessed_urls), chunk_size):
            chunk_end = min(chunk_start + chunk_size, len(unprocessed_urls))
            chunk_urls = unprocessed_urls[chunk_start:chunk_end]
            
            logger.info(f"\n📦 Procesando chunk {chunk_start//chunk_size + 1} ({len(chunk_urls)} URLs)")
            
            # Procesar chunk con ThreadPoolExecutor limitado
            stats = extractor.extract_talks_batch(chunk_urls, batch_size)
            
            total_processed += stats['total']
            total_successful += stats['successful']
            total_failed += stats['failed']
            
            # Log progreso
            logger.info(f"✅ Chunk completado: {stats['successful']}/{stats['total']} exitosos")
            
            # Pausa entre chunks para permitir que el sistema respire
            if chunk_end < len(unprocessed_urls):
                logger.info(f"⏸️  Pausa de {args.pause_between_batches}s para estabilizar sistema...")
                time.sleep(args.pause_between_batches)
                
                # Verificar recursos del sistema
                needs_pause, resources = check_system_resources()
                logger.info(f"📊 Recursos: {resources}")
                if needs_pause:
                    logger.warning("⚠️  Sistema bajo stress - pausa adicional de 30s")
                    time.sleep(30)
                
                # Forzar limpieza de memoria
                gc.collect()
        
        # Resumen final
        duration = time.time() - start_time
        duration_str = f"{duration/60:.1f} minutos" if duration > 60 else f"{duration:.1f} segundos"
        
        logger.info("\n" + "=" * 70)
        logger.info("📊 RESULTADOS DE LA EXTRACCIÓN ESTABLE")
        logger.info("=" * 70)
        logger.info(f"✅ Procesados exitosamente: {total_successful}/{total_processed}")
        logger.info(f"❌ Fallidos: {total_failed}")
        logger.info(f"⏱️  Tiempo total: {duration_str}")
        
        if total_successful > 0:
            avg_time = duration / total_successful
            logger.info(f"📈 Tiempo promedio por discurso: {avg_time:.1f} segundos")
        
        success_rate = (total_successful / total_processed) * 100 if total_processed > 0 else 0
        logger.info(f"🎯 Tasa de éxito: {success_rate:.1f}%")
        
        logger.info("\n✨ ¡Extracción estable completada!")
        
    except KeyboardInterrupt:
        logger.info("\n⚠️  Proceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Error en extracción estable: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
