import { retrieve } from './airtable_retrieve';
import { base } from './airtable_connection';
import { sleep } from './util';
import minimist from 'minimist';


function cleanEntry(sheet: string, id: string): Promise<void> {
  return new Promise<void>((resolve, reject) => {
    base(sheet).destroy([id], (err: Error, deletedRecords: any) => {
      if (err) {
        reject(err);
        return;
      }
      resolve();
    });
  });
}

export async function clean(sheet: string, field: string, value: string) {
  let count = 0;
  let retrievedEntries = await retrieve(sheet, field, value);

  for (let i = 0; i < retrievedEntries.length; i++) {
    await sleep(300);
    await cleanEntry(sheet, retrievedEntries[i].id);
    count++;
  }

  console.log('Deleted', count, 'records.');
};


if (require.main === module) {
  //node airtable_clean.js --sheet="Table 9" --field="Name" --value="test"

  const args = minimist(process.argv.slice(2));
  clean(args.sheet, args.field, args.value);
}
