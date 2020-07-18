import { retrieve } from './airtable_retrieve';
import { base } from './airtable_connection';
import { sleep } from './util';
import minimist from 'minimist';

const args = minimist(process.argv.slice(2));
//node airtable_clean.js --sheet="Table 9" --field="Name" --value="test"


function cleanEntry(id: string) {
  return new Promise<void>((resolve) => {
    base(args.sheet).destroy([id], (err: Error, deletedRecords: any) => {
      if (err) {
        console.error(err);
        return;
      }
      resolve();
    });
  });
}


async function clean() {
  let count = 0;
  let retrievedEntries = await retrieve(args.sheet, args.field, args.value);

  for (let i = 0; i < retrievedEntries.length; i++) {
    await sleep(300);
    await cleanEntry(retrievedEntries[i].id);
    count++;
  }

  console.log('Deleted', count, 'records.');
};


clean();
