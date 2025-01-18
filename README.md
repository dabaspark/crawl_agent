# Website to Markdown Crawler

A simple crawler that converts websites into markdown files using their sitemap.xml. Built with Crawl4AI.

## Prerequisites

- Python 3.9+
- Node.js (for sitemap generation)

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

# Install Node.js dependencies (for sitemap generation)
npm install -g sitemap-generator
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

Simple usage:
```bash
python website_to_markdown.py
```


To change the target website or output directory, edit `config.py`:
```python
# Edit these values in config.py
BASE_URL = "https://ai.pydantic.dev"  # Change to your target website
OUTPUT_DIR = "output"                 # Change output location if needed
```

The script will:
1. Check if sitemap.xml exists at the given URL
2. Generate sitemap if none exists
3. Convert pages to markdown
4. Create status report and combined output


## Configuration

Edit `config.py` to change:
```python
DEFAULT_SITEMAP_URL = "https://ai.pydantic.dev/sitemap.xml"
MAX_CONCURRENT_REQUESTS = 5  # Adjust based on your needs
DEFAULT_OUTPUT_DIR = "output"
```

## Features

- Automatic sitemap.xml detection and generation
- Parallel webpage crawling
- Markdown conversion with progress tracking
- Detailed crawling statistics
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

- website should not use dynamic javascript or modern framework to be able to generate sitemap.xml
- JavaScript-rendered content might need extra wait time to crawl
- Large sites might need adjustment of concurrent request limits

## How it Works

1. Checks if target website has sitemap.xml
2. If no sitemap found, generates one using sitemap-generator
3. Uses sitemap to discover all pages
4. Converts pages to markdown in parallel
5. Generates status report and combined output
