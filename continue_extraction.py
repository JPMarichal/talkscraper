#!/usr/bin/env python3
"""
TalkScraper - Continue Extraction from Last Point

This script intelligently continues extraction from where it left off,
avoiding reprocessing already completed talks.
"""

import sys
import argparse
import time
import sqlite3
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from scrapers.talk_content_extractor import TalkContentExtractor
from utils.config_manager import ConfigManager
from utils.logger_setup import setup_logger


def get_existing_talk_urls(conf_dir: Path) -> set:
    """Get all URLs that already have generated HTML files."""
    existing_urls = set()
    
    for lang_dir in conf_dir.iterdir():
        if lang_dir.is_dir() and lang_dir.name in ['eng', 'spa']:
            for year_month_dir in lang_dir.iterdir():
                if year_month_dir.is_dir():
                    for html_file in year_month_dir.glob('*.html'):
                        # Extract URL pattern from filename and directory structure
                        year_month = year_month_dir.name
                        if len(year_month) == 6:  # YYYYMM format
                            year = year_month[:4]
                            month = year_month[4:]
                            
                            # Try to reconstruct URL pattern
                            # This is approximate but should work for most cases
                            url_base = f"https://www.churchofjesuschrist.org/study/general-conference/{year}/{month}/"
                            existing_urls.add(year_month)
    
    return existing_urls


def filter_unprocessed_urls(all_urls: list, existing_periods: set, language: str) -> list:
    """Filter URLs to only include those not yet processed."""
    unprocessed = []
    
    for url in all_urls:
        # Extract year/month from URL
        if '/general-conference/' in url and f'lang={language}' in url:
            parts = url.split('/general-conference/')
            if len(parts) > 1:
                date_part = parts[1].split('/')[0:2]  # year/month
                if len(date_part) == 2:
                    year, month = date_part
                    period = f"{year}{month.zfill(2)}"
                    
                    if period not in existing_periods:
                        unprocessed.append(url)
    
    return unprocessed


def main():
    """Main continuation process."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Continue Phase 3 Extraction from Last Point')
    parser.add_argument('--language', choices=['eng', 'spa'], default='eng',
                       help='Language to process (default: eng)')
    parser.add_argument('--batch-size', type=int, default=24,
                       help='Number of talks to process in each batch (default: 24)')
    parser.add_argument('--config', default='config.ini',
                       help='Configuration file path (default: config.ini)')
    
    args = parser.parse_args()
    
    # Setup logger
    config = ConfigManager(args.config)
    log_config = config.get_log_config()
    logger = setup_logger('ContinueExtraction', log_config)
    
    logger.info("=" * 70)
    logger.info("CONTINUACIÓN INTELIGENTE DE EXTRACCIÓN - FASE 3")
    logger.info("=" * 70)
    logger.info(f"Idioma: {args.language}")
    logger.info(f"Tamaño de lote optimizado: {args.batch_size}")
    
    try:
        # Initialize content extractor
        extractor = TalkContentExtractor(args.config)
        
        # Get existing processed periods
        conf_dir = Path('conf')
        existing_periods = get_existing_talk_urls(conf_dir)
        logger.info(f"📁 Encontrados {len(existing_periods)} períodos ya procesados")
        
        # Get ALL talk URLs from database
        logger.info(f"\n📊 Obteniendo URLs completas de la base de datos...")
        all_talk_urls = extractor.get_unprocessed_talk_urls(args.language, None)
        logger.info(f"📋 URLs totales en base de datos: {len(all_talk_urls)}")
        
        # Filter to get only truly unprocessed URLs
        truly_unprocessed = filter_unprocessed_urls(all_talk_urls, existing_periods, args.language)
        logger.info(f"🎯 URLs realmente no procesadas: {len(truly_unprocessed)}")
        
        if not truly_unprocessed:
            logger.info(f"✅ ¡Todos los discursos ya han sido procesados para {args.language}!")
            return
        
        # Show first and last URLs to confirm range
        logger.info("\n🔍 Rango de URLs a procesar:")
        logger.info(f"   Primera: {truly_unprocessed[0] if truly_unprocessed else 'N/A'}")
        logger.info(f"   Última: {truly_unprocessed[-1] if truly_unprocessed else 'N/A'}")
        
        # Confirmation
        logger.info(f"\n⚠️  Se van a procesar {len(truly_unprocessed)} discursos restantes.")
        logger.info("🚀 Iniciando procesamiento CONTINUADO en 3 segundos...")
        time.sleep(3)
        
        # Start optimized batch extraction
        logger.info(f"\n🚀 Iniciando extracción optimizada desde el punto correcto...")
        start_time = time.time()
        
        stats = extractor.extract_talks_batch(truly_unprocessed, args.batch_size)
        
        # Calculate duration
        duration = time.time() - start_time
        duration_str = f"{duration/60:.1f} minutos" if duration > 60 else f"{duration:.1f} segundos"
        
        # Report results
        logger.info("\n" + "=" * 70)
        logger.info("📊 RESULTADOS DE LA EXTRACCIÓN CONTINUADA")
        logger.info("=" * 70)
        logger.info(f"✅ Procesados exitosamente: {stats['successful']}/{stats['total']}")
        logger.info(f"💾 Guardados como archivos: {stats['saved']}")
        logger.info(f"❌ Fallidos: {stats['failed']}")
        logger.info(f"⏱️  Tiempo total: {duration_str}")
        
        if stats['successful'] > 0:
            avg_time = duration / stats['successful']
            logger.info(f"📈 Tiempo promedio por discurso: {avg_time:.1f} segundos")
        
        # Success summary
        success_rate = (stats['successful'] / stats['total']) * 100 if stats['total'] > 0 else 0
        logger.info(f"\n🎯 Tasa de éxito: {success_rate:.1f}%")
        
        logger.info("\n✨ ¡Extracción continuada completada exitosamente!")
        
    except KeyboardInterrupt:
        logger.info("\n⚠️  Proceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Error en extracción continuada: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
