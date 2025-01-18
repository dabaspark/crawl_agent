# Website to Markdown Crawler

A simple crawler that converts websites into markdown files using their sitemap.xml. Built with Crawl4AI.

## Tech Stack

- **Crawl4AI**: Main crawler engine, handles JavaScript rendering and content extraction
- **Python 3.9+**: Async implementation for parallel crawling
- **aiohttp**: For handling async HTTP requests
- **lxml**: XML parsing for sitemaps

## Setup

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Output Structure

The script creates the following structure:
```
output/
├── pages/          # Individual markdown files for each page
│   ├── page1.md
│   └── page2.md
├── collected.md    # All pages combined into one file
└── status.md      # Crawling status and results
```

## Usage

Basic usage:
```bash
python website_to_markdown.py
```

The script will:
1. Read the sitemap from the configured URL
2. Convert each page to markdown in output/pages/
3. Generate status report in output/status.md
4. Create combined markdown in output/collected.md

## Configuration

Edit `config.py` to change:
```python
DEFAULT_SITEMAP_URL = "https://ai.pydantic.dev/sitemap.xml"
MAX_CONCURRENT_REQUESTS = 5  # Adjust based on your needs
DEFAULT_OUTPUT_DIR = "output"
```

## Features

- Progress tracking with status bars
- Detailed statistics including:
  - Success rate
  - Total pages crawled
  - Word count
  - Failure analysis
- Parallel processing with visual progress
- Combined output with status tracking

## Notes

- Uses async/await for concurrent processing
- Handles rate limiting through semaphores
- Creates clean markdown without JS artifacts
- File names are derived from URL paths

## Status Tracking

The status.md file shows:
- Timestamp of each crawl
- URL processed
- Success/failure status
- Output filename

## Statistics

The status.md file includes:
- Overall success rate
- Total pages processed
- Word counts
- Failure analysis
- Detailed crawl log

## Known limitations:

- Requires a valid sitemap.xml
- JavaScript-rendered content might need extra wait time
- Large sites might need adjustment of concurrent request limits
- Large files might take longer to combine in collected.md
