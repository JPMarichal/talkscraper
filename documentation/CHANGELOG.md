# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added - Milestone 6: Metadata Integrity and Extraction Hardening (2025-10-25)

#### Core Improvements
- **Data Validation**: New `_validate_talk_data()` method ensures talks have required fields (title, author, content with min 100 chars) before being marked as processed
- **Enhanced Logging**: Added comprehensive logging for Selenium failures and extraction errors to `processing_log` table
- **Metadata Backup**: Improved `backup_existing_html_metadata()` method with:
  - Robust HTML element validation (handles missing title, author, calling gracefully)
  - Correct conference_session format conversion (YYYYMM → YYYY-MM)
  - Progress logging every 100 files
  - Detailed error reporting

#### Tools & Scripts
- **Metadata Restoration CLI**: New `scripts/restore_metadata.py` script for populating `talk_metadata` table from existing HTML files
  - Options: `--dry-run`, `--language`, `--conference`, `--verbose`
  - Comprehensive statistics reporting
  - Successfully processed 6839 HTML files → 3763 unique metadata records

#### Testing
- **Integration Tests**: Added 7 new integration tests in `tests/integration/test_talk_extractors_integration.py`
  - Metadata backup flow validation
  - Talk data validation and incomplete data handling
  - HTML parsing and conference_session format conversion
  - Selenium failure logging
  - Complete extraction flow with validation
- **Test Coverage**: All 40 unit tests and 7 integration tests pass

#### Database
- Enhanced `processing_log` tracking for:
  - `selenium_note_extraction` failures
  - `talk_content_extraction` errors
  - Retry attempts with detailed messages

### Changed
- **Extraction Flow**: Modified `extract_complete_talk()` to log failures to database
- **Processing Logic**: Updated `_process_talk_attempt()` to validate data before marking talks as processed
- **Error Handling**: Improved error handling in `_backup_talk_metadata()` with better error messages

### Fixed
- **Conference Session Format**: Fixed conversion from directory name format (198510) to database format (1985-10)
- **Missing Elements**: Fixed AttributeError when HTML elements (title, author, calling) are missing
- **Metadata Persistence**: Ensured metadata is properly saved to `talk_metadata` table even on partial extraction failures

## Metrics
- **HTML Files Processed**: 6,839
- **Unique Metadata Records**: 3,763
  - English: 2,595 talks
  - Spanish: 1,168 talks
- **Processing Success Rate**: 100% (0 errors during restoration)
- **Test Pass Rate**: 100% (47/47 tests passing)

## Notes
- The difference between HTML files (6,839) and metadata records (3,763) is due to duplicate URLs (same talk in different formats/locations)
- The UNIQUE(url) constraint in `talk_metadata` table prevents duplicates, which is correct behavior
