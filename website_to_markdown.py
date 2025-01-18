import os
import sys
import asyncio
import requests
import subprocess
from xml.etree import ElementTree
from typing import List, Dict
from urllib.parse import urlparse, urljoin
from datetime import datetime
from tqdm.asyncio import tqdm
from collections import Counter
from dataclasses import dataclass, field
import re  # Add this import at the top

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from config import (
    MAX_CONCURRENT_REQUESTS, 
    BROWSER_CONFIG, 
    REQUEST_TIMEOUT,
    BASE_URL,
    OUTPUT_DIR
)

@dataclass
class CrawlStats:
    total_urls: int = 0
    successful_urls: int = 0
    total_words: int = 0
    failures: Counter = field(default_factory=Counter)  # Fix: use default_factory for mutable Counter

    @property
    def success_rate(self) -> float:
        return (self.successful_urls / self.total_urls * 100) if self.total_urls > 0 else 0

def update_status_file(stats: CrawlStats, output_dir: str, log_entry: tuple = None):
    """Update status file with statistics and optionally add a log entry."""
    status_file = os.path.join(output_dir, 'status.md')
    
    # Create file with headers if it doesn't exist
    if not os.path.exists(status_file):
        with open(status_file, 'w', encoding='utf-8') as f:
            f.write("# Crawling Results\n\n")
            f.write("## Overall Statistics\n\n")
            f.write("## Failure Types\n\n")
            f.write("## Detailed Crawl Log\n\n")
            f.write("| Timestamp | URL | Status | Filename |\n")
            f.write("|-----------|-----|--------|----------|\n")
    
    # Read existing content
    with open(status_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update statistics section
    stats_section = (
        "## Overall Statistics\n\n"
        f"- Success Rate: {stats.success_rate:.2f}%\n"
        f"- Total Pages: {stats.total_urls}\n"
        f"- Successful Crawls: {stats.successful_urls}\n"
        f"- Total Words: {stats.total_words:,}\n\n"
    )
    
    # Update failure types section
    failure_section = "## Failure Types\n\n"
    if stats.failures:
        for error, count in stats.failures.items():
            failure_section += f"- {error}: {count}\n"
    failure_section += "\n"
    
    # Split content at section markers
    parts = content.split("## ")
    header = parts[0]
    log_section = "## Detailed Crawl Log\n\n" + parts[-1].split("Detailed Crawl Log\n\n")[1]
    
    # Add new log entry if provided
    if log_entry:
        timestamp, url, status, filename = log_entry
        log_section += f"| {timestamp} | {url} | {status} | {filename} |\n"
    
    # Combine all sections
    updated_content = (
        header +
        stats_section +
        failure_section +
        log_section
    )
    
    # Write updated content
    with open(status_file, 'w', encoding='utf-8') as f:
        f.write(updated_content)

def create_status_file(output_dir: str):
    """Create or reset the status.md file with headers."""
    status_file = os.path.join(output_dir, 'status.md')
    with open(status_file, 'w', encoding='utf-8') as f:
        f.write("# Crawling Status\n\n")
        f.write("| Timestamp | URL | Status | Filename |\n")
        f.write("|-----------|-----|--------|----------|\n")

def collect_markdown_files(pages_dir: str, output_dir: str):
    """Combine all markdown files into a single collected.md file."""
    collected_file = os.path.join(output_dir, 'collected.md')
    with open(collected_file, 'w', encoding='utf-8') as outfile:
        for filename in sorted(os.listdir(pages_dir)):
            if filename.endswith('.md'):
                filepath = os.path.join(pages_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as infile:
                    outfile.write(f"\n\n## {filename[:-3]}\n\n")
                    outfile.write(infile.read())
                    outfile.write("\n\n---\n")

async def crawl_parallel(urls: List[str], output_dir: str):
    """Crawl multiple URLs in parallel with a concurrency limit."""
    pages_dir = os.path.join(output_dir, 'pages')
    os.makedirs(pages_dir, exist_ok=True)
    stats = CrawlStats(total_urls=len(urls))
    
    browser_config = BrowserConfig(
        headless=BROWSER_CONFIG["headless"],
        verbose=BROWSER_CONFIG["verbose"],
        extra_args=BROWSER_CONFIG["extra_args"],
    )
    crawl_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)

    # Create the crawler instance
    crawler = AsyncWebCrawler(config=browser_config)
    await crawler.start()

    try:
        # Create a semaphore to limit concurrency
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
        
        async def process_url(url: str):
            async with semaphore:
                result = await crawler.arun(
                    url=url,
                    config=crawl_config,
                    session_id="session1"
                )
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                path = urlparse(url).path
                filename = path.strip('/').replace('/', '_') or 'index'
                filepath = f"{pages_dir}/{filename}.md"
                
                if result.success:
                    content = result.markdown_v2.raw_markdown
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    stats.successful_urls += 1
                    stats.total_words += len(content.split())
                    # Add success entry to log
                    update_status_file(stats, output_dir, (timestamp, url, "Success", f"{filename}.md"))
                    return True, url, filename
                else:
                    stats.failures[result.error_message] += 1
                    # Add failure entry to log
                    update_status_file(stats, output_dir, (timestamp, url, f"Failed: {result.error_message}", "N/A"))
                    return False, url, "N/A"

        # Show progress bar for crawling
        results = await tqdm.gather(*[process_url(url) for url in urls],
                                  desc="Crawling pages")
        
        # Update status file with results
        update_status_file(stats, output_dir)
        
        # Show progress bar for combining files
        with tqdm(desc="Combining markdown files") as pbar:
            collect_markdown_files(pages_dir, output_dir)
            pbar.update(1)
        
        print(f"\nFinal Results:")
        print(f"Success Rate: {stats.success_rate:.2f}%")
        print(f"Total Pages: {stats.total_urls}")
        print(f"Total Words: {stats.total_words:,}")
        
    finally:
        await crawler.close()

def get_sitemap_urls(sitemap_location: str) -> List[str]:
    """Get URLs from website sitemap."""
    try:
        # Handle remote sitemap URLs vs local files
        if sitemap_location.startswith('http'):
            response = requests.get(sitemap_location, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            content = response.text
        else:
            # Local file
            with open(sitemap_location, 'r', encoding='utf-8') as f:
                content = f.read()
            
        root = ElementTree.fromstring(content)
        
        # Try standard sitemap format first
        urls = root.findall(".//url/loc")
        if not urls:
            # Try alternate namespace format
            namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            urls = root.findall('.//ns:loc', namespace)
        
        return [url.text for url in urls if url.text]
    except Exception as e:
        print(f"Error reading sitemap: {e}")
        return []

def check_sitemap_exists(base_url: str) -> bool:
    """Check if sitemap.xml exists at the given URL."""
    sitemap_url = urljoin(base_url, 'sitemap.xml')
    try:
        response = requests.head(sitemap_url, timeout=REQUEST_TIMEOUT)
        return response.status_code == 200
    except Exception:
        return False

def generate_sitemap(base_url: str) -> str:
    """Generate sitemap.xml using Node.js script."""
    print("Generating sitemap.xml...")
    generator_dir = os.path.join(os.path.dirname(__file__), 'sitemap_generator', 'simple_generator')
    
    try:
        # Run generator from its directory
        result = subprocess.run(
            ['node', 'generate-sitemap.js'],
            capture_output=True,
            text=True,
            check=True,
            cwd=generator_dir  # Set working directory for the script
        )
        print(result.stdout)
        return os.path.join(generator_dir, 'sitemap.xml')
    except subprocess.CalledProcessError as e:
        print(f"Error generating sitemap: {e.stderr}")
        raise

def update_sitemapper_config(url: str):
    """Update the config.js for sitemapper-for-js."""
    config_path = os.path.join(
        os.path.dirname(__file__),
        'sitemap_generator',
        'sitemapper-for-js',
        'config.js'
    )
    
    domain = urlparse(url).netloc + urlparse(url).path.rstrip('/')
    
    with open(config_path, 'r') as f:
        content = f.read()
    
    # Update base URL
    content = re.sub(
        r"base: '.*'",
        f"base: '{url}'",
        content
    )
    
    # Update urls array
    content = re.sub(
        r"urls: \[.*?\]",
        f"urls: ['{url}']",
        content,
        flags=re.DOTALL
    )
    
    # Update strictPresence
    content = re.sub(
        r"strictPresence: '.*'",
        f"strictPresence: '{domain}'",
        content
    )
    
    with open(config_path, 'w') as f:
        f.write(content)

def generate_sitemap_advanced(base_url: str) -> str:
    """Generate sitemap using sitemapper-for-js for dynamic websites."""
    print("Attempting advanced sitemap generation...")
    generator_dir = os.path.join(os.path.dirname(__file__), 'sitemap_generator', 'sitemapper-for-js')
    
    try:
        # Update config with current URL
        update_sitemapper_config(base_url)
        
        # Run the advanced generator
        result = subprocess.run(
            ['npm', 'start'],
            capture_output=True,
            text=True,
            check=True,
            cwd=generator_dir
        )
        print(result.stdout)
        return os.path.join(generator_dir, 'sitemap.xml')
    except subprocess.CalledProcessError as e:
        print(f"Error generating sitemap with advanced generator: {e.stderr}")
        raise

async def main():
    print(f"Processing website: {BASE_URL}")
    print(f"Output directory: {OUTPUT_DIR}")
    
    # Try existing sitemap first
    if check_sitemap_exists(BASE_URL):
        sitemap_url = urljoin(BASE_URL, 'sitemap.xml')
        print(f"Found existing sitemap at: {sitemap_url}")
        try:
            urls = get_sitemap_urls(sitemap_url)
            print(f"Successfully parsed remote sitemap")
        except Exception as e:
            print(f"Error with remote sitemap: {e}")
            urls = []
    else:
        # Try simple generator first
        print("No sitemap.xml found. Trying simple generator...")
        update_generator_url(BASE_URL)
        sitemap_path = generate_sitemap(BASE_URL)
        print(f"Generated sitemap at: {sitemap_path}")
        urls = get_sitemap_urls(sitemap_path)
        
        # If simple generator didn't find enough URLs, try advanced generator
        if len(urls) <= 2:
            print("Simple generator failed to find enough URLs. Trying advanced generator...")
            sitemap_path = generate_sitemap_advanced(BASE_URL)
            print(f"Generated advanced sitemap at: {sitemap_path}")
            urls = get_sitemap_urls(sitemap_path)
    
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    if not urls:
        print("No URLs found to crawl")
        return
    
    print(f"Found {len(urls)} URLs to crawl")
    await crawl_parallel(urls, OUTPUT_DIR)

def update_generator_url(url: str):
    """Update the URL in generate-sitemap.js."""
    generator_path = os.path.join(
        os.path.dirname(__file__), 
        'sitemap_generator', 
        'simple_generator',
        'generate-sitemap.js'
    )
    with open(generator_path, 'r') as f:
        content = f.read()
    
    # Replace the URL in the JavaScript file using Python's re
    updated_content = re.sub(
        r"const url = '.*';",
        f"const url = '{url}';",
        content
    )
    
    with open(generator_path, 'w') as f:
        f.write(updated_content)

if __name__ == "__main__":
    asyncio.run(main())