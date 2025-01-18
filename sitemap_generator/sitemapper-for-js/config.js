/*
 * *
 *  Copyright 2014 Comcast Cable Communications Management, LLC
 *
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *  http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 * /
 */

 /*
 * ** IMPORTANT ** RENAME THIS FILE TO 'config.js' BEFORE RUNNING THE SCRIPT
 */

module.exports  = {
    base: 'https://mujoco.readthedocs.io/en/stable/', // base url of the website
    urls: ['https://mujoco.readthedocs.io/en/stable/'],
    strictPresence: 'mujoco.readthedocs.io/en/stable', // Crawl links only if this is present
    ignoreStrings: [
        'genindex',
        '_sources',
        '_static',
        'search.html',
        'search?',
        '_images/',  // Add this to filter out image URLs
        '.png',      // Add this to filter out PNG files
        '.gif',      // Add this to filter out GIF files
        '.jpg',      // Add this to filter out JPG files
        'rtd.io',    // Add this to filter out readthedocs.io tracking
        '#'          // Add this to filter out anchor links
    ],
    autoCrawl: true, // Changed to false for manual crawling
    crawlLevel: 1, // Documentation typically isn't too deep
    pageLoad: {
        waitUntil: 'networkidle2', // Changed from networkidle0 to networkidle2
        timeout: 100000, // Increased timeout to 100 seconds
        retryLimit: 3,    // Add retry limit for failed requests
        batchSize: 5    // Number of URLs to process in parallel
    },
    disableHashRoutes: true,
    sortBy: 'asc'
}