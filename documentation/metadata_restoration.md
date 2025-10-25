# Metadata Restoration Guide

## Overview

This guide explains how to restore metadata from existing HTML files to the `talk_metadata` database table. This is useful when:
- You have previously generated HTML files but the database is incomplete
- You need to rebuild the metadata table
- You want to populate metadata for historical talks

## Prerequisites

- Python 3.8 or higher
- All dependencies installed (`pip install -r requirements.txt`)
- Existing HTML files in the `conf/` directory
- Valid `config.ini` file

## Directory Structure

HTML files should be organized as follows:
```
conf/
├── eng/
│   ├── 197104/  (YYYYMM format)
│   │   ├── Talk Title (Author Name).html
│   │   └── ...
│   ├── 197110/
│   └── ...
└── spa/
    ├── 199004/
    └── ...
```

## Using the Restoration Script

### Basic Usage

Restore all metadata from HTML files:
```bash
python scripts/restore_metadata.py
```

### Dry Run Mode

Preview what would be done without making changes:
```bash
python scripts/restore_metadata.py --dry-run
```

### Filter by Language

Process only English or Spanish talks:
```bash
python scripts/restore_metadata.py --language eng
python scripts/restore_metadata.py --language spa
```

### Filter by Conference

Process only a specific conference (future enhancement):
```bash
python scripts/restore_metadata.py --conference 202504
```

### Verbose Output

Enable detailed debug logging:
```bash
python scripts/restore_metadata.py --verbose
```

### Combining Options

```bash
python scripts/restore_metadata.py --language eng --verbose --dry-run
```

## HTML File Requirements

Each HTML file must contain:
- `<h1>` tag with the talk title
- `.author` class element with the author name
- `.calling` class element with the author's calling (optional)
- `<a href="...">` tag with the original talk URL
- Directory name in YYYYMM format (e.g., 202504 for April 2025)

### Example HTML Structure

```html
<!DOCTYPE html>
<html lang="eng">
<head>
    <title>Talk Title - Author Name</title>
</head>
<body>
    <div class="header">
        <h1>Talk Title</h1>
        <div class="author">Elder Author Name</div>
        <div class="calling">Of the Quorum of the Twelve Apostles</div>
    </div>
    <div class="content">...</div>
    <div class="extraction-info">
        <a href="https://www.churchofjesuschrist.org/study/general-conference/2025/04/talk-title?lang=eng">
            URL
        </a>
    </div>
</body>
</html>
```

## Output and Statistics

After completion, the script displays:
- Total files processed
- Number of errors encountered
- Metadata records by language
- Recent conferences with talk counts

### Example Output

```
============================================================
Metadata Restoration Script
============================================================
Initializing with config: config.ini
Starting metadata restoration from HTML files...
Processed 100 HTML files...
Processed 200 HTML files...
...
Backup complete: 6839 files processed, 0 errors
Metadata restoration complete!

Final Statistics:
Metadata records by language:
  eng: 2595 talks
  spa: 1168 talks

Recent conferences:
  2025-04 (eng): 3 talks
  2025-04 (spa): 1 talks
  2024-10 (eng): 1 talks
  ...
============================================================
```

## Database Schema

The script populates the `talk_metadata` table:

```sql
CREATE TABLE talk_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    calling TEXT,
    note_count INTEGER,
    language TEXT,
    year TEXT,
    conference_session TEXT,  -- Format: YYYY-MM
    backup_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(url)
);
```

## Error Handling

The script handles common errors gracefully:

### Missing Elements
- **Missing title**: Logs warning, skips file
- **Missing author**: Logs warning, skips file
- **Missing calling**: Uses "Unknown" as default
- **Missing URL**: Logs warning, skips file

### Invalid Directory Format
Files in directories not matching YYYYMM format are skipped with a warning.

### Duplicate URLs
The `UNIQUE(url)` constraint prevents duplicate entries. If a URL already exists, the INSERT OR REPLACE operation updates the existing record.

## Verification

After restoration, verify the data:

```bash
# Check total metadata records
sqlite3 talkscraper_state.db "SELECT COUNT(*) FROM talk_metadata;"

# Check by language
sqlite3 talkscraper_state.db "SELECT language, COUNT(*) FROM talk_metadata GROUP BY language;"

# View recent conferences
sqlite3 talkscraper_state.db "
  SELECT conference_session, language, COUNT(*) as talks 
  FROM talk_metadata 
  GROUP BY conference_session, language 
  ORDER BY conference_session DESC 
  LIMIT 10;
"

# Check for specific conference
sqlite3 talkscraper_state.db "
  SELECT title, author, conference_session 
  FROM talk_metadata 
  WHERE conference_session = '2025-04' 
  LIMIT 5;
"
```

## Troubleshooting

### Problem: Script reports many errors
**Solution**: Check HTML file structure. Ensure all required elements exist.

### Problem: Fewer metadata records than HTML files
**Explanation**: This is normal. The UNIQUE(url) constraint prevents duplicates. Some HTML files may reference the same talk URL.

### Problem: Conference session format incorrect
**Explanation**: Directory names must be in YYYYMM format (e.g., 202504). The script converts this to YYYY-MM format (e.g., 2025-04).

### Problem: Special characters in filenames
**Explanation**: The script handles Unicode characters correctly. Ensure your terminal supports UTF-8 encoding.

## Programmatic Usage

You can also use the restoration function directly in your code:

```python
from core.talk_content_extractor import TalkContentExtractor

# Initialize extractor
extractor = TalkContentExtractor('config.ini', skip_notes=True)

# Run restoration
extractor.backup_existing_html_metadata()

# Check results
stats = extractor.db.get_processing_stats()
print(f"Metadata records: {stats['metadata']}")
```

## Best Practices

1. **Backup First**: Backup your database before running restoration
   ```bash
   cp talkscraper_state.db talkscraper_state.db.backup
   ```

2. **Dry Run**: Always run with `--dry-run` first to verify behavior

3. **Monitor Logs**: Check `logs/restore_metadata.log` for detailed information

4. **Incremental Updates**: Run periodically to update metadata for new HTML files

5. **Validate After**: Always verify the data after restoration

## Integration with Main Workflow

The restoration script complements the normal extraction workflow:

1. **Normal Extraction**: `TalkContentExtractor.extract_complete_talk()` automatically backs up metadata
2. **Restoration**: Use `restore_metadata.py` to fill gaps from existing HTML files
3. **Verification**: Check `talk_metadata` table for completeness

## Performance

- **Speed**: Processes ~100-200 files per second
- **Memory**: Low memory usage (streaming file processing)
- **Database**: Uses INSERT OR REPLACE for efficient updates
- **Logging**: Minimal I/O with periodic progress updates

## Related Documentation

- [CHANGELOG.md](CHANGELOG.md) - Recent changes and improvements
- Main README - Overall project documentation
- Database schema documentation
