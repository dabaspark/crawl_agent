const SitemapGenerator = require('sitemap-generator');
const path = require('path');

// URL of your website
const url = 'http://adjtomo.github.io/pyflex/';

// Path to save the sitemap.xml file
const filepath = path.join(__dirname, 'sitemap.xml');

console.log(`Starting sitemap generation for: ${url}`);
console.log(`Output will be saved to: ${filepath}`);

// Create generator with more options
const generator = SitemapGenerator(url, {
  filepath: filepath,
  maxEntriesPerFile: 50000,
  stripQuerystring: true,
  lastMod: true,
  changeFreq: 'weekly',
  maxDepth: 0,  // Crawl all levels
  timeout: 60000,  // Longer timeout
});

// Counter for the number of URLs found
let urlCount = 0;

// Register event listeners
generator.on('add', (url) => {
  urlCount++;
  console.log(`[${urlCount}] Added URL: ${url}`);
});

generator.on('done', () => {
  console.log(`\nSitemap generation completed!`);
  console.log(`Total URLs found: ${urlCount}`);
  console.log(`Sitemap saved to: ${filepath}`);
  process.exit(0);  // Ensure clean exit
});

generator.on('error', (error) => {
  console.error('Error generating sitemap:', error);
  process.exit(1);  // Exit with error code
});

// Start the crawler
try {
  console.log('Crawler starting...\n');
  generator.start();
} catch (error) {
  console.error('Failed to start crawler:', error);
  process.exit(1);
}