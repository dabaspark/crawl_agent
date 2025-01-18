# Website to Markdown Crawler

A crawler that converts any website (static or dynamic) into markdown files for documentation or RAG purposes.

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

## Supported Website Types

### Static Websites
- Basic HTML/CSS websites
- GitHub Pages
- Simple documentation sites

### Dynamic Websites
- Single Page Applications (SPAs)
- React/Vue.js based sites
- Complex routing systems
- JavaScript-heavy applications

### Documentation Platforms
- ReadTheDocs
- Custom documentation sites
- API documentation
- Technical documentation

## Prerequisites

- Python 3.9+
- Node.js (for automatic sitemap generation)

## Setup

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
cd sitemap_generator/simple_generator
npm install -S sitemap-generator
cd ../sitemapper-for-js
npm install
cd ../..
```

## Usage

Change the target base url of the website, edit `config.py`:
```python
# Edit these values in config.py
BASE_URL = "http://adjtomo.github.io/pyflex/"  # Change to your target website
```

Then:
```bash
python website_to_markdown.py
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

## Status Tracking

The status.md file shows:
- Timestamp of each crawl
- URL processed
- Success/failure status
- Output filename


# Technical Details

## How it Works

## Intelligent Crawling Strategy
1. **Existing Sitemap Detection**
   - First checks for existing sitemap.xml
   - Directly uses if found (fastest method)

2. **Simple Static Generation**
   - Uses sitemap-generator for basic websites
   - Fast and efficient for static content

3. **Advanced Dynamic Generation**
   - Falls back to sitemapper-for-js for complex sites
   - Handles JavaScript frameworks (React, Vue, etc.)
   - Configurable filters and crawl settings

4. Converts pages to markdown in parallel
5. Generates status report and combined output


## Notes

- Uses async/await for concurrent processing
- Handles rate limiting through semaphores
- Creates clean markdown without JS artifacts
- File names are derived from URL paths

## Tech Stack

### Core Technologies
- **Crawl4AI**: Main crawler engine for HTML to Markdown conversion

### Sitemap Generation Libraries
- **[sitemap-generator](https://github.com/lgraubner/sitemap-generator)**: For static websites
- **[sitemapper-for-js](https://github.com/dabaspark/sitemapper-for-js)**: For dynamic/JS-heavy websites
  - Uses Puppeteer for JavaScript rendering
  - Handles complex routing and SPAs
  - Configurable crawl depth and filters

### Supporting Libraries
- **puppeteer**: Web scraping (via sitemapper-for-js)

## Project Structure
```
crawler-agent/
├── website_to_markdown.py  # Main script
├── config.py              # Configuration
├── requirements.txt       # Python dependencies
├── output/               # Generated markdown files
│   ├── pages/           # Individual pages
│   ├── collected.md     # Combined output
│   └── status.md        # Crawling status
└── sitemap_generator/    # Sitemap generation tools
    └── simple_generator/ # Node.js sitemap generator
        └── generate-sitemap.js
```


## Tested Websites

### With existing sitemap.xml
- https://ai.pydantic.dev/
  - Clean documentation site with existing sitemap
  - Direct crawling using existing sitemap.xml

### Without sitemap.xml (Simple sites)
- http://adjtomo.github.io/pyflex/
  - GitHub Pages documentation
  - Successfully generated sitemap using simple-sitemap-generator

### Without sitemap.xml (Complex/Dynamic sites)
- https://mujoco.readthedocs.io/en/stable/
  - ReadTheDocs documentation with dynamic content
  - Required advanced sitemapper-for-js generator
  - Successfully handled JavaScript-rendered content

## Known limitations:
- JavaScript-rendered content might need extra wait time to crawl
- Large sites might need adjustment of concurrent request limits



## Troubleshooting
### Sitemap Generation Issues
If the sitemap generator freezes:

Test the generator directly for simple_generator and change the target base url at `generate-sitemap.js`:
```bash
cd sitemap_generator/simple_generator
node generate-sitemap.js
```
if it failed please consult: **[sitemap-generator](https://github.com/lgraubner/sitemap-generator)**

or for the advanced generator and change the target base url at `config.js` :
```bash
cd sitemap_generator/sitemapper-for-js
npm start
```
if it failed please consult: **[sitemapper-for-js](https://github.com/dabaspark/sitemapper-for-js)**

The generator should show progress with URL counts and complete with a success message.


