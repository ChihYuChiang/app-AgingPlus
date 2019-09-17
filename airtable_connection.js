const fs = require("fs");
const yaml = require('js-yaml');
const Airtable = require("airtable");
const cred = yaml.safeLoad(fs.readFileSync('./ref/credential.yml', 'utf8'));

exports.base = new Airtable({ apiKey: cred.Airtable.apiKey }).base(cred.Airtable.baseId);