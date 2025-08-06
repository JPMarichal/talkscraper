#!/usr/bin/env python3
"""
TalkScraper - Phase 3: Complete Content Extraction

This script runs the complete content extraction process including:
- Static content extraction (title, author, calling, content)
- Dynamic note extraction using Selenium
- HTML file generation with proper formatting and navigation
- Database tracking and batch processing

Usage:
    python phase3_extraction.py [--language eng|spa] [--limit N] [--batch-size N]
"""

import sys
import argparse
import time
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from scrapers.talk_content_extractor import TalkContentExtractor
from utils.config_manager import ConfigManager
from utils.logger_setup import setup_logger


def main():
    """Main Phase 3 extraction process."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Phase 3: Complete Content Extraction')
    parser.add_argument('--language', choices=['eng', 'spa'], default='eng',
                       help='Language to process (default: eng)')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of talks to process')
    parser.add_argument('--batch-size', type=int, default=12,
                       help='Number of talks to process in each batch (default: 12 - optimized for 64GB RAM)')
    parser.add_argument('--config', default='config.ini',
                       help='Configuration file path (default: config.ini)')
    
    args = parser.parse_args()
    
    # Setup logger
    config = ConfigManager(args.config)
    log_config = config.get_log_config()
    logger = setup_logger('Phase3Extraction', log_config)
    
    logger.info("=" * 60)
    logger.info("FASE 3: EXTRACCIÓN COMPLETA DE CONTENIDO")
    logger.info("=" * 60)
    logger.info(f"Idioma: {args.language}")
    logger.info(f"Límite: {args.limit if args.limit else 'Sin límite'}")
    logger.info(f"Tamaño de lote: {args.batch_size}")
    
    try:
        # Initialize content extractor
        extractor = TalkContentExtractor(args.config)
        
        # Get unprocessed talk URLs
        logger.info(f"\n📊 Obteniendo URLs no procesadas para idioma: {args.language}")
        talk_urls = extractor.get_unprocessed_talk_urls(args.language, args.limit)
        
        if not talk_urls:
            logger.info(f"✅ No hay URLs pendientes para procesar en {args.language}")
            return
        
        logger.info(f"📋 Encontradas {len(talk_urls)} URLs para procesar")
        
        # Show sample of URLs to be processed
        logger.info("\n🔍 Muestra de URLs a procesar:")
        for i, url in enumerate(talk_urls[:5], 1):
            logger.info(f"   {i}. {url}")
        if len(talk_urls) > 5:
            logger.info(f"   ... y {len(talk_urls) - 5} más")
        
        # Ask for confirmation if processing many URLs
        if len(talk_urls) > 10:
            logger.info(f"\n⚠️  Se van a procesar {len(talk_urls)} discursos.")
            logger.info("💡 Esto puede tomar tiempo considerable...")
            logger.info("🚀 Iniciando procesamiento en 3 segundos...")
            time.sleep(3)
        
        # Start batch extraction
        logger.info(f"\n🚀 Iniciando extracción en lotes...")
        start_time = time.time()
        
        stats = extractor.extract_talks_batch(talk_urls, args.batch_size)
        
        # Calculate duration
        duration = time.time() - start_time
        duration_str = f"{duration/60:.1f} minutos" if duration > 60 else f"{duration:.1f} segundos"
        
        # Report results
        logger.info("\n" + "=" * 60)
        logger.info("📊 RESULTADOS DE LA EXTRACCIÓN")
        logger.info("=" * 60)
        logger.info(f"✅ Procesados exitosamente: {stats['successful']}/{stats['total']}")
        logger.info(f"💾 Guardados como archivos: {stats['saved']}")
        logger.info(f"❌ Fallidos: {stats['failed']}")
        logger.info(f"⏱️  Tiempo total: {duration_str}")
        
        if stats['successful'] > 0:
            avg_time = duration / stats['successful']
            logger.info(f"📈 Tiempo promedio por discurso: {avg_time:.1f} segundos")
        
        # Mark processed URLs in database
        if stats['successful'] > 0:
            logger.info(f"\n📝 Marcando URLs como procesadas en la base de datos...")
            processed_count = 0
            for url in talk_urls[:stats['successful']]:
                try:
                    extractor.mark_talk_processed(url, True)
                    processed_count += 1
                except Exception as e:
                    logger.warning(f"Error marcando {url} como procesado: {e}")
            
            logger.info(f"✅ Marcadas {processed_count} URLs como procesadas")
        
        # Success summary
        success_rate = (stats['successful'] / stats['total']) * 100 if stats['total'] > 0 else 0
        logger.info(f"\n🎯 Tasa de éxito: {success_rate:.1f}%")
        
        if stats['successful'] > 0:
            logger.info(f"📁 Archivos guardados en: conf/{args.language}/")
            logger.info("🔗 Los archivos incluyen:")
            logger.info("   • Contenido completo con formato HTML")
            logger.info("   • Enlaces de notas funcionales")
            logger.info("   • Navegación interna")
            logger.info("   • Estilos profesionales")
        
        logger.info("\n✨ ¡Fase 3 completada exitosamente!")
        
    except KeyboardInterrupt:
        logger.info("\n⚠️  Proceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Error en Fase 3: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
