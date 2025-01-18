# SITEMAP GENERATOR FOR SPA (SINGLE PAGE APPLICATION)

> This is a fork of [Comcast/sitemapper-for-js](https://github.com/Comcast/sitemapper-for-js) with enhanced reliability, error handling, and modern JavaScript practices.

### Why This Fork?

This fork improves upon the original with:
- Modern async/await patterns throughout the codebase
- Improved browser resource management with proper cleanup
- Robust error handling and recovery mechanisms
- Efficient batch processing with configurable sizes
- Better memory management and cleanup procedures
- Enhanced URL extraction and validation
- Cleaner XML output format
- Comprehensive logging and debugging capabilities
- Browser instance reuse for better performance

## Core Changes

Major improvements have been made to these key files:
- `crawler.js`: Enhanced with async/await, better error handling, and batch processing
- `web.js`: Improved browser management, retry mechanisms, and resource cleanup
- `files.js`: Modernized file operations and cleaner XML output
- `rules.js`: More efficient URL filtering and validation
- `server.js`: Added proper cleanup handlers and better resource management

For detailed technical changes, see [changes_flag.md](./changes_flag.md).

### About

Sitemaps are simple XML documents consisting of links of all pages in a website. This provides additional information about the page to search engine crawlers to categories the type of content and serve it to the users based on their search keywords. 

Most commonly used sitemap generators works well with websites with multiple pages that are built with PHP, ASP.NET or any old-school technologies since the browser reloads everytime the user navigates through different pages. Wherease, websites that rely heavily on Javascript (Like Angular / React / Vuejs ) will not reload during page navigation and only the `view` changes. This makes the existing generators difficult to capture different routes and create a sitemap out of it. 

This Sitemap generator, built with `puppeteer (Google Chrome's Headless Chrome Node API) ` works well with Javascript based websites in creating Sitemaps


### Setup & Configuration

`npm install`

To start generating:

`npm start`

**config.js Example**

```js
module.exports = {
    base: 'https://mujoco.readthedocs.io/en/stable/',
    urls: [
        'https://mujoco.readthedocs.io/en/stable/',
        'https://mujoco.readthedocs.io/en/stable/overview.html'
    ],
    strictPresence: 'mujoco.readthedocs.io/en/stable/',
    ignoreStrings: [
        'genindex',
        '_sources',
        '_static',
        'search.html',
        'search?',
        '_images/',
        '.png',
        '.gif',
        '.jpg',
        'rtd.io',
        '#'
    ],
    autoCrawl: false,
    crawlLevel: 1,
    pageLoad: {
        waitUntil: 'networkidle2',
        timeout: 100000,
        retryLimit: 3
    },
    disableHashRoutes: true,
    sortBy: 'asc'
}
```

### Enhanced Features

1. **Modern JavaScript Implementation**
   - Full async/await support
   - Promise-based file operations
   - Better parallel processing
   - Configurable batch processing

2. **Improved Browser Management**
   - Browser instance reuse
   - Proper cleanup on interruption
   - Better resource management
   - Configurable timeouts and retries

3. **Enhanced Error Handling**
   - Comprehensive try-catch blocks
   - Retry mechanisms for failed requests
   - Graceful error recovery
   - Process cleanup on failures

4. **Better URL Processing**
   - Improved link extraction
   - Better URL validation
   - Efficient filtering mechanisms
   - More reliable depth calculation

5. **Performance Optimizations**
   - Parallel batch processing
   - Configurable crawl limits
   - Memory usage improvements
   - Reduced function call overhead

### Original Configuration Options

**base**

`base: 'https://www.xfinity.com'`

Website that you want to create sitemap for

**urls (only for manual Crawling)**

Array of urls that you wanted to crawl. Links present in the mentional html pages will **not** be recursively called in this

**strictPresence**

Add the url to XML only if this string presents

**ignoreStrings**

List of urls/strings you wanted to ignore in the links you are adding to Sitemap

**autoCrawl**

Enable/Disable Auto Crawling feature. Auto-crawling takes more time than manual crawl. Largely depends on the complexity of website


**crawlLevel(only for auto-crawl)**

Mention number of child routes you would like to crawl in case of auto-crawling

E.g.: 
Lets assume the base url `https://abc.com/`, 

`crawlLevel=1` would crawl in pattern  `https://abc.com/<any-path>`
`crawlLevel=2` would crawl in pattern  `https://abc.com/<any-path>/<any-path>`


**pageLoad**

Page load settings inherited from puppeteer configuration

https://github.com/GoogleChrome/puppeteer/blob/master/docs/api.md#pagegotourl-options


**disableHashRoutes**

Ignore any routes with `#` in it

E.g.:

Avoids these urls

`https://abc.com/#section2`
`https://abc.com/#/section2`
`https://abc.com/about#section4`




## License

This repo is licensed under [Apache License 2.0](LICENSE).



