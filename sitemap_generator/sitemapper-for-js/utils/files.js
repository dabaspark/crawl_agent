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

const fs = require('fs').promises;
const log = require('./log');

const filesService = {
    async createXml(links) {
        try {
            const xmlStart = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n';
            const xmlEnd = '</urlset>';
            
            let xmlContent = xmlStart;
            links.forEach(link => {
                xmlContent += `  <url>\n    <loc>${link}</loc>\n    <changefreq>weekly</changefreq>\n  </url>\n`;
            });
            xmlContent += xmlEnd;

            const urlCount = links.length;
            await fs.writeFile('sitemap.xml', xmlContent);
            log.log('Sitemap file created successfully');
            log.log(`Total URLs in sitemap: ${urlCount}`);
            return true;
        } catch (error) {
            console.error('Error creating sitemap:', error);
            throw error;
        }
    }
};

module.exports = filesService;