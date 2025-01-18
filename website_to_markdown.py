import os
import sys
import asyncio
import requests
from xml.etree import ElementTree
from typing import List, Dict
from urllib.parse import urlparse
from datetime import datetime

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from config import (
    MAX_CONCURRENT_REQUESTS, 
    BROWSER_CONFIG, 
    REQUEST_TIMEOUT,
    DEFAULT_SITEMAP_URL,
    DEFAULT_OUTPUT_DIR
)

def update_status_file(url: str, status: str, filename: str, output_dir: str):
    """Update the status.md file with crawling results."""
    status_file = os.path.join(output_dir, 'status.md')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open(status_file, 'a', encoding='utf-8') as f:
        f.write(f"| {timestamp} | {url} | {status} | {filename} |\n")

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
    create_status_file(output_dir)
    
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
                path = urlparse(url).path
                filename = path.strip('/').replace('/', '_') or 'index'
                filepath = f"{pages_dir}/{filename}.md"
                
                if result.success:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(result.markdown_v2.raw_markdown)
                    update_status_file(url, "Success", f"{filename}.md", output_dir)
                    print(f"Saved markdown to: {filepath}")
                else:
                    update_status_file(url, f"Failed: {result.error_message}", "N/A", output_dir)
                    print(f"Failed: {url} - Error: {result.error_message}")
        
        # Process all URLs in parallel with limited concurrency
        await asyncio.gather(*[process_url(url) for url in urls])
        
        # Collect all markdown files after crawling
        collect_markdown_files(pages_dir, output_dir)
        
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