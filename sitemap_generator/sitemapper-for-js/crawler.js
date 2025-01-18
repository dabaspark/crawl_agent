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

const rulesService = require('./utils/rules');
const filesService = require('./utils/files');
const webService = require('./utils/web');
const log = require('./utils/log');
const _ = require('underscore');
const config = require('./config');
const parallel = require('paralleljs');

const crawler = {

    counter: 0,

    allUrls: [],

    processes: [],

    processesCompleted: [],

    dataFetched: 0,

    baseUrlHashes: config.base.split('/').length,

    async getXml(xmUrl, limit) {
        try {
            //log.log(`Queuing ${xmUrl}`);
            const data = await webService.getWeb(xmUrl);
            log.log(`Data received for ${xmUrl}`);
            this.counter = this.counter + 1;
            this.allUrls = _.union(this.allUrls, rulesService.checkRules(data));
            
            if (this.counter >= limit) {
                log.log('All URLs processed, creating sitemap...');
                await filesService.createXml(rulesService.sortLinks(this.allUrls));
                log.log('Sitemap created successfully!');
                setTimeout(() => process.exit(0), 1000); // Give time for file writing
            }
        } catch (error) {
            console.error(`Failed processing ${xmUrl}: ${error.message}`);
            this.counter = this.counter + 1;
            if (this.counter >= limit) {
                log.log('All URLs processed (with some errors), creating sitemap...');
                await filesService.createXml(rulesService.sortLinks(this.allUrls));
                log.log('Sitemap created successfully!');
                setTimeout(() => process.exit(0), 1000);
            }
        }
    },

    /*
    * 1. Feed the base Url and fetch HTML
    * 2. Remove url from 'process' array
    * 3. Push the url to 'processCompleted' 
    * 4. Filter the fetched urls for the following
    *   A) Urls already processed stored in 'processCompleted'
    *   B) Urls that are already present in queue stored in 'processes'
    *   C) Ignoring urls based on levels
    * 5. Push all the remaining urls to 'processes'
    * 6. autoFetch again
    * 7. If processes are empty, create sitemap
    */
    async autoFetch() {
        if (this.processes.length === 0) {
            log.log('No more URLs to process, creating sitemap...');
            await filesService.createXml(rulesService.sortLinks(this.allUrls));
            log.log('Sitemap created successfully!');
            setTimeout(() => process.exit(0), 1000);
            return;
        }

        // Use batchSize from config
        const batchSize = config.pageLoad.batchSize || 5; // Default to 5 if not specified
        const urlsToProcess = this.processes.splice(0, batchSize);
        
        // Create array of promises for parallel processing
        const promises = urlsToProcess.map(async (xmUrl) => {
            this.counter++;
            this.processesCompleted.push(xmUrl);

            try {
                const data = await webService.getWeb(xmUrl);
                log.log(`Data received for ${xmUrl}`);
                const newUrls = rulesService.checkRules(data);
                this.allUrls = _.union(this.allUrls, newUrls);
                this.dataFetched++;
                
                await this.queueUrls(newUrls);
            } catch (error) {
                console.error(`Error processing ${xmUrl}:`, error);
                this.dataFetched++;
            }
        });

        // Wait for all URLs in batch to complete
        await Promise.all(promises);

        // Continue with next batch
        if (this.processes.length > 0) {
            await this.autoFetch();
        } else if (this.counter === this.dataFetched) {
            // All processing complete
            log.log('No more URLs to process, creating sitemap...');
            await filesService.createXml(rulesService.sortLinks(this.allUrls));
            log.log('Sitemap created successfully!');
            setTimeout(() => process.exit(0), 1000);
        }
    },

    async queueUrls(urls) {        
        // Filter Urls already processed stored in 'processCompleted'
        const removingCompleted = _.uniq(_.without(urls, ...this.processesCompleted));
        const removingQueued = _.without(removingCompleted, ...this.processes);

        const removingIngoreLevels = _.filter(removingQueued, url => {
            const urlDepth = url.split('/').length - this.baseUrlHashes;
            return urlDepth <= config.crawlLevel;
        });

        const urlsIgnored = _.difference(urls, removingIngoreLevels);
        this.processesCompleted.push(...urlsIgnored);
        this.processes = _.uniq([...this.processes, ...removingIngoreLevels]);

        // Remove parallel processing which was causing issues
        return Promise.resolve();
    }
}

module.exports = crawler;