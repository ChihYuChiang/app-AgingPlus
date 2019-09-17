const { retrieve } = require('./airtable_retrieve.js');

retrieve('Table 9', 'Name', 'test').then((retrievedEntries) => {
  console.log(retrievedEntries);
});