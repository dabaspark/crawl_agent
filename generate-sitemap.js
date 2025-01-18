const SitemapGenerator = require('sitemap-generator');
const path = require('path');

// URL of your website
const url = 'http://adjtomo.github.io/pyflex/';

// Path to save the sitemap.xml file
const filepath = path.join(__dirname, 'sitemap', 'sitemap.xml');

// Create generator
const generator = SitemapGenerator(url, {
  filepath: filepath,
  maxEntriesPerFile: 50000,
  stripQuerystring: true,
  lastMod: true,
  changeFreq: 'weekly',
});

// Counter for the number of URLs found
let urlCount = 0;

// Register event listeners
generator.on('add', (url) => {
  urlCount++; // Increment the counter for each URL added
  console.log(`Added URL: ${url}`);
});

generator.on('done', () => {
  console.log(`Sitemap generated successfully! Total URLs found: ${urlCount}`);
});

generator.on('error', (error) => {
  console.error('Error generating sitemap:', error);
});

// Start the crawler
generator.start();