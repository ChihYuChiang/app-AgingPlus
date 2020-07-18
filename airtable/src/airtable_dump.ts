import * as fs from 'fs';
import { Parser } from 'json2csv';
import { retrieve, Entry } from './airtable_retrieve';
import minimist from 'minimist';

const args = minimist(process.argv.slice(2));
//node airtable_dump.js --sheet="Table 9" --field="Name" --value="test"


retrieve(args.sheet, args.field, args.value).then((retrievedEntries: Entry[]) => {
  const fields = Object.keys(retrievedEntries[0]);
  const json2csvParser = new Parser({ fields });
  const table = json2csvParser.parse(retrievedEntries);

  try {
    fs.writeFile('./data/output.csv', table, 'utf8', () => {
      console.log('CSV file has been saved.');
    });
  } catch (err) {
    console.error('An error occurred while writing the Object to File.');
    throw err;
  }
});
