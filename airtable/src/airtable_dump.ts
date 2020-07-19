import * as fs from 'fs';
import { Parser } from 'json2csv';
import { retrieve, Entry } from './airtable_retrieve';
import minimist from 'minimist';


// TODO: output path as parameter
export async function dump(sheet: string, field: string, value: string): Promise<void> {
  await retrieve(sheet, field, value)
    .then(async (retrievedEntries: Entry[]) => {
      const fields = Object.keys(retrievedEntries[0]);
      const json2csvParser = new Parser({ fields });
      const table = json2csvParser.parse(retrievedEntries);
  
      try {
        await fs.promises.writeFile('./data/output.csv', table, 'utf8');
        console.log('CSV file has been saved.');
      } catch (err) {
        console.error('An error occurred while writing the Object to File.');
        throw err;
      }
    });
};


if (require.main === module) {
  //node airtable_dump.js --sheet="Table 9" --field="Name" --value="test"

  const args = minimist(process.argv.slice(2));
  dump(args.sheet, args.field, args.value);
}
