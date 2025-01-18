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

const puppeteer = require('puppeteer');
const config = require('../config');

const webService = {
    browser: null,

    async initBrowser() {
        if (!this.browser) {
            this.browser = await puppeteer.launch({
                headless: true,
                args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
            });
        }
        return this.browser;
    },

    async getWeb(url, retryCount = 0) {
        let page;
        try {
            const browser = await this.initBrowser();
            page = await browser.newPage();
            
            await page.setDefaultNavigationTimeout(config.pageLoad.timeout);
            await page.goto(url, {
                waitUntil: ['networkidle2', 'domcontentloaded'],
                timeout: config.pageLoad.timeout
            });

            await page.waitForSelector('a');

            const hrefs = await page.evaluate(() => {
                return Array.from(document.querySelectorAll('a[href]'))
                    .map(a => a.href)
                    .filter(href => href && 
                           href.startsWith('http') && 
                           !href.startsWith('javascript:'));
            });

            await page.close();
            return hrefs;
        } catch (error) {
            if (page) await page.close();
            
            if (retryCount < (config.pageLoad.retryLimit || 3)) {
                return await this.getWeb(url, retryCount + 1);
            }
            
            console.error(`Error processing ${url}: ${error.message}`);
            return [];
        }
    },

    async cleanup() {
        if (this.browser) {
            await this.browser.close();
            this.browser = null;
        }
    }
};

// Add cleanup on process exit
process.on('exit', () => {
    if (webService.browser) {
        webService.cleanup();
    }
});

module.exports = webService;