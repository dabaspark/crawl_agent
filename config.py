# Crawler Configuration
MAX_CONCURRENT_REQUESTS = 5
BROWSER_CONFIG = {
    "headless": True,
    "verbose": False,
    "extra_args": ["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"]
}

# Fixed defaults (edit these values to change target site and output location)
BASE_URL = "http://adjtomo.github.io/pyflex/"
OUTPUT_DIR = "output"

# Request Configuration
REQUEST_TIMEOUT = 30  # seconds
