# Website to Markdown Crawler

A simple crawler that converts Documentation Websites into markdown files. Built with Crawl4AI.

## Prerequisites

- Python 3.9+
- Node.js (for automatic sitemap generation)

## Tech Stack

- **Crawl4AI**: Main crawler engine, handles JavaScript rendering and content extraction
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
BASE_URL = "http://adjtomo.github.io/pyflex/"  # Change to your target website
OUTPUT_DIR = "output"                 # Change output location if needed
```

## How it Works

1. Checks if target website has sitemap.xml
2. If no sitemap found, generates one using sitemap-generator
3. Uses sitemap to discover all pages
4. Converts pages to markdown in parallel
5. Generates status report and combined output


## Features

- Automatic sitemap.xml detection and generation
- Parallel webpage crawling
- HTML to Markdown conversion 
- Detailed crawling statistics including:
  - Success rate
  - Total pages crawled
  - Word count
  - Failure analysis
- Combined output to be used for RAG LLM applications

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

## Known limitations:

- website should not use dynamic javascript or modern framework (ex. React) to be able to generate sitemap.xml
- JavaScript-rendered content might need extra wait time to crawl
- Large sites might need adjustment of concurrent request limits

