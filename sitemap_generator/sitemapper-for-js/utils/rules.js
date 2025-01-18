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

const config = require('../config');

const rulesService = {
    checkRules(urls) {
        if (!urls || !Array.isArray(urls)) {
            console.log('No valid URLs to process');
            return [];
        }

        //console.log(`Processing ${urls.length} URLs through rules`);
        
        return urls.filter(url => {
            // Must contain the strict presence string
            const hasStrictPresence = url.includes(config.strictPresence);
            
            // Must not contain any of the ignore strings
            const hasNoIgnoreStrings = !config.ignoreStrings.some(ignore => 
                url.toLowerCase().includes(ignore.toLowerCase())
            );

            /*
            // Log filtered URLs for debugging
            if (!hasStrictPresence) {
                console.log(`Filtered out (strictPresence): ${url}`);
            }
            if (!hasNoIgnoreStrings) {
                console.log(`Filtered out (ignoreStrings): ${url}`);
            }
            */

            return hasStrictPresence && hasNoIgnoreStrings;
        });
    },
    
    notExemptions(url) {
        for (let i = 0; i < config.ignoreStrings.length; i++) {

            if (config.disableHashRoutes && url.includes('#')) {
                return false;
            }

            if (!url.includes(config.strictPresence)) {
                return false;
            }

            if (url.includes(config.ignoreStrings[i])) {
                return false;
            }

            if (i === config.ignoreStrings.length - 1) {
                return true;
            }
        }

    },

    doNotIgnore(url) {
        return this.notExemptions(url);
    },

    sortLinks(links) {
        switch (config.sortBy) {
            case 'asc':
                console.log('Sorting in asc');
                return links.sort();
            case 'dsc':
                console.log('Sorting in dsc');
                return links.sort().reverse();
            default:
                console.log('No sort');
                return links;
        }
    }
}

module.exports = rulesService;