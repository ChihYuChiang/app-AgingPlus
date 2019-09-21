const { retrieve } = require('./airtable_retrieve.js');
const { base } = require('./airtable_connection.js');
const { sleep } = require('./util.js');
const args = require('minimist')(process.argv.slice(2));
//node airtable_clean.js --sheet="Table 9" --field="Name" --value="test"

function cleanEntry(id) {
  return new Promise((resolve) => {
    base(args.sheet).destroy([id], (err, deletedRecords) => {
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