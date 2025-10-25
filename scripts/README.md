# TalkScraper Scripts

This directory contains utility scripts for managing the TalkScraper database and content.

## Available Scripts

### restore_metadata.py

Restores metadata from existing HTML files to the `talk_metadata` database table.

**Usage:**
```bash
# Basic restoration
python scripts/restore_metadata.py

# Dry run (preview only)
python scripts/restore_metadata.py --dry-run

# Restore only English talks
python scripts/restore_metadata.py --language eng

# Verbose output
python scripts/restore_metadata.py --verbose
```

**See:** [Metadata Restoration Guide](../documentation/metadata_restoration.md) for detailed documentation.

## Adding New Scripts

When adding new scripts to this directory:

1. Make the script executable: `chmod +x scripts/your_script.py`
2. Add shebang line: `#!/usr/bin/env python3`
3. Include comprehensive docstring with usage examples
4. Add argument parsing with `--help` option
5. Update this README with script description
6. Add documentation to `documentation/` directory if needed
