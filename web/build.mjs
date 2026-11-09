import { readFileSync, mkdirSync, writeFileSync } from 'node:fs';
const catalog = JSON.parse(readFileSync('data/catalog.json', 'utf8'));
const html = readFileSync('index.html', 'utf8');
const zip = readFileSync('data/portable-agents.zip').toString('base64');
const runtime = readFileSync('runtime.mjs', 'utf8');
mkdirSync('dist/server', {recursive:true});
writeFileSync('dist/server/index.js', `const catalog=${JSON.stringify(catalog)};\nconst html=${JSON.stringify(html)};\nconst zip=${JSON.stringify(zip)};\n${runtime}\nexport default {fetch: (request) => handle(request, {catalog, html, zip})};\n`);
console.log('Built standalone Worker.');
