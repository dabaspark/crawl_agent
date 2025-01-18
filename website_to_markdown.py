import os
import sys
import asyncio
import requests
from xml.etree import ElementTree
from typing import List, Dict
from urllib.parse import urlparse
from datetime import datetime
from tqdm.asyncio import tqdm
from collections import Counter
from dataclasses import dataclass, field

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from config import (
    MAX_CONCURRENT_REQUESTS, 
    BROWSER_CONFIG, 
    REQUEST_TIMEOUT,
    DEFAULT_SITEMAP_URL,
    DEFAULT_OUTPUT_DIR
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

def get_sitemap_urls(sitemap_url: str) -> List[str]:
    """Get URLs from website sitemap."""
    try:
        response = requests.get(sitemap_url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        # Parse the XML
        root = ElementTree.fromstring(response.content)
        
        # Extract all URLs from the sitemap
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = [loc.text for loc in root.findall('.//ns:loc', namespace)]
        
        return urls
    except Exception as e:
        print(f"Error fetching sitemap: {e}")
        return []

async def main():
    sitemap_url = DEFAULT_SITEMAP_URL
    output_dir = DEFAULT_OUTPUT_DIR
    
    print(f"Using default settings:")
    print(f"Sitemap URL: {sitemap_url}")
    print(f"Output directory: {output_dir}")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get URLs from sitemap
    urls = get_sitemap_urls(sitemap_url)
    if not urls:
        print("No URLs found to crawl")
        return
    
    print(f"Found {len(urls)} URLs to crawl")
    await crawl_parallel(urls, output_dir)

if __name__ == "__main__":
    asyncio.run(main())