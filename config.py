# Crawler Configuration
MAX_CONCURRENT_REQUESTS = 5
BROWSER_CONFIG = {
    "headless": True,
    "verbose": False,
    "extra_args": ["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"]
}

# File System Configuration
DEFAULT_OUTPUT_DIR = "output"

# URL Configuration
DEFAULT_SITEMAP_URL = "https://ai.pydantic.dev/sitemap.xml"  # Changed to a real example

# Request Configuration
REQUEST_TIMEOUT = 30  # seconds
