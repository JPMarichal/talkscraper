#!/usr/bin/env python3
"""
TalkScraper - Continuación EQUILIBRADA con control de CPU

Configuración optimizada para equilibrio velocidad/recursos:
- 16 hilos concurrentes para mantener velocidad
- Control inteligente de CPU para evitar picos del 100%
- Pausas dinámicas basadas en carga del sistema
- Chrome optimizado para reducir uso de CPU
- Procesamiento por chunks con recuperación de memoria
"""

import sys
import argparse
import time
import gc
import psutil
import threading
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


class CPUMonitor:
    """Monitor de CPU para controlar la carga del sistema."""
    
    def __init__(self, max_cpu_percent=85, check_interval=5):
        self.max_cpu_percent = max_cpu_percent
        self.check_interval = check_interval
        self.should_pause = False
        self.monitoring = True
        self.monitor_thread = None
        
    def start_monitoring(self, logger):
        """Iniciar monitoreo en hilo separado."""
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(logger,), daemon=True)
        self.monitor_thread.start()
        
    def _monitor_loop(self, logger):
        """Loop de monitoreo de CPU."""
        while self.monitoring:
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                if cpu_percent > self.max_cpu_percent:
                    if not self.should_pause:
                        logger.warning(f"🔥 CPU alta ({cpu_percent:.1f}%) - activando pausas adaptativas")
                        self.should_pause = True
                elif cpu_percent < (self.max_cpu_percent - 10):  # Histéresis
                    if self.should_pause:
                        logger.info(f"✅ CPU normalizada ({cpu_percent:.1f}%) - desactivando pausas")
                        self.should_pause = False
                
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error en monitor CPU: {e}")
                break
                
    def stop_monitoring(self):
        """Detener monitoreo."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
            
    def get_adaptive_pause(self):
        """Retornar pausa adaptativa basada en carga de CPU."""
        if self.should_pause:
            return 3  # Pausa de 3 segundos cuando CPU está alta
        return 0.5  # Pausa mínima normal


def check_system_resources():
    """Verificar recursos del sistema."""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        return cpu_percent, memory.percent
    except Exception:
        return 0, 0


def main():
    """Proceso principal de continuación equilibrada."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Continuación EQUILIBRADA con control de CPU')
    parser.add_argument('--batch-size', type=int, default=16,
                       help='Hilos concurrentes (default: 16 - equilibrado)')
    parser.add_argument('--config', default='config.ini',
                       help='Archivo de configuración')
    parser.add_argument('--max-cpu', type=int, default=85,
                       help='CPU máximo antes de pausas adaptativas (default: 85%)')
    
    args = parser.parse_args()
    
    # Setup logger
    config = ConfigManager(args.config)
    log_config = config.get_log_config()
    logger = setup_logger('ContinueExtractionBalanced', log_config)
    
    logger.info("=" * 70)
    logger.info("CONTINUACIÓN EQUILIBRADA - CONTROL INTELIGENTE DE CPU")
    logger.info("=" * 70)
    logger.info(f"Hilos concurrentes: {args.batch_size}")
    logger.info(f"CPU máximo: {args.max_cpu}%")
    
    # Inicializar monitor de CPU
    cpu_monitor = CPUMonitor(max_cpu_percent=args.max_cpu)
    
    try:
        # Verificar recursos iniciales
        cpu_percent, ram_percent = check_system_resources()
        logger.info(f"📊 Recursos iniciales: CPU {cpu_percent:.1f}%, RAM {ram_percent:.1f}%")
        
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
        
        # Calcular estimación de tiempo equilibrada
        estimated_time_per_talk = 3.5  # Equilibrio entre velocidad y estabilidad
        total_estimated_minutes = (len(unprocessed_urls) * estimated_time_per_talk) / 60
        
        logger.info(f"\n⚠️  Se van a procesar {len(unprocessed_urls)} discursos restantes.")
        logger.info(f"🕐 Tiempo estimado: {total_estimated_minutes:.1f} minutos (~{total_estimated_minutes/60:.1f} horas)")
        logger.info("⚖️  Configuración EQUILIBRADA - velocidad con control de recursos")
        
        # Iniciar monitor de CPU
        cpu_monitor.start_monitoring(logger)
        logger.info("🔍 Monitor de CPU activado")
        
        logger.info("🚀 Iniciando procesamiento EQUILIBRADO en 3 segundos...")
        time.sleep(3)
        
        # Procesar en lotes con control adaptativo
        batch_size = args.batch_size
        total_processed = 0
        total_successful = 0
        total_failed = 0
        start_time = time.time()
        
        logger.info(f"\n🚀 Iniciando extracción equilibrada desde el punto correcto...")
        
        # Procesar en chunks más pequeños para mejor control
        chunk_size = 40  # Chunks más pequeños para mejor control de CPU
        
        for chunk_start in range(0, len(unprocessed_urls), chunk_size):
            chunk_end = min(chunk_start + chunk_size, len(unprocessed_urls))
            chunk_urls = unprocessed_urls[chunk_start:chunk_end]
            
            chunk_num = chunk_start // chunk_size + 1
            total_chunks = (len(unprocessed_urls) + chunk_size - 1) // chunk_size
            
            logger.info(f"\n📦 Procesando chunk {chunk_num}/{total_chunks} ({len(chunk_urls)} URLs)")
            
            # Verificar CPU antes del chunk
            cpu_percent, ram_percent = check_system_resources()
            logger.info(f"📊 Pre-chunk: CPU {cpu_percent:.1f}%, RAM {ram_percent:.1f}%")
            
            # Procesar chunk
            chunk_start_time = time.time()
            stats = extractor.extract_talks_batch(chunk_urls, batch_size)
            chunk_duration = time.time() - chunk_start_time
            
            total_processed += stats['total']
            total_successful += stats['successful']
            total_failed += stats['failed']
            
            # Log progreso del chunk
            chunk_speed = stats['successful'] / chunk_duration if chunk_duration > 0 else 0
            logger.info(f"✅ Chunk {chunk_num} completado: {stats['successful']}/{stats['total']} exitosos ({chunk_speed:.2f} talks/s)")
            
            # Pausa adaptativa entre chunks
            if chunk_end < len(unprocessed_urls):
                adaptive_pause = cpu_monitor.get_adaptive_pause()
                logger.info(f"⏸️  Pausa adaptativa: {adaptive_pause}s")
                time.sleep(adaptive_pause)
                
                # Verificar recursos post-chunk
                cpu_percent, ram_percent = check_system_resources()
                logger.info(f"📊 Post-chunk: CPU {cpu_percent:.1f}%, RAM {ram_percent:.1f}%")
                
                # Forzar limpieza de memoria cada ciertos chunks
                if chunk_num % 3 == 0:
                    logger.info("🧹 Limpieza de memoria...")
                    gc.collect()
        
        # Detener monitor de CPU
        cpu_monitor.stop_monitoring()
        
        # Resumen final
        duration = time.time() - start_time
        duration_str = f"{duration/60:.1f} minutos" if duration > 60 else f"{duration:.1f} segundos"
        
        logger.info("\n" + "=" * 70)
        logger.info("📊 RESULTADOS DE LA EXTRACCIÓN EQUILIBRADA")
        logger.info("=" * 70)
        logger.info(f"✅ Procesados exitosamente: {total_successful}/{total_processed}")
        logger.info(f"❌ Fallidos: {total_failed}")
        logger.info(f"⏱️  Tiempo total: {duration_str}")
        
        if total_successful > 0:
            avg_time = duration / total_successful
            avg_speed = total_successful / duration if duration > 0 else 0
            logger.info(f"📈 Tiempo promedio por discurso: {avg_time:.1f} segundos")
            logger.info(f"🚀 Velocidad promedio: {avg_speed:.2f} talks/segundo")
        
        success_rate = (total_successful / total_processed) * 100 if total_processed > 0 else 0
        logger.info(f"🎯 Tasa de éxito: {success_rate:.1f}%")
        
        logger.info("\n✨ ¡Extracción equilibrada completada!")
        
    except KeyboardInterrupt:
        logger.info("\n⚠️  Proceso interrumpido por el usuario")
        cpu_monitor.stop_monitoring()
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Error en extracción equilibrada: {e}")
        cpu_monitor.stop_monitoring()
        sys.exit(1)


if __name__ == "__main__":
    main()
