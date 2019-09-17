const { retrieve } = require('./airtable_retrieve.js');
const { base } = require('./airtable_connection.js');

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function cleanEntry(id) {
  return new Promise((resolve) => {
    base(table).destroy([id], (err, deletedRecords) => {
      if (err) {
        console.error(err);
        return;
      }
      resolve();
    });
  });
}

const table = 'Table 9';
async function clean() {
  let count = 0;
  let retrievedEntries = await retrieve(table, 'Name', 'test');

  for (i = 0; i < retrievedEntries.length; i++) {
    await sleep(500);
    await cleanEntry(retrievedEntries[i].id);
    count++;
  }

  console.log('Deleted', count, 'records.');
};

clean();