const { base } = require('./airtable_connection.js');
const { sleep } = require('./util.js');

exports.retrieve = function(targetSheet, targetField, targetValue) {
  return new Promise((resolve, reject) => {
    let table = [];
    base(targetSheet)
      .select({
        view: "Grid view",
        cellFormat: "json"
      })
      .eachPage(
        async function page(records, fetchNextPage) {
          // This function (`page`) will get called for each page of records.
    
          records.forEach((record) => {
            let entry = {
                "id": record.id,
                "createdTime": record._rawJson.createdTime,
                ...record.fields
            };
            table.push(entry);
          });
    
          // To fetch the next page of records, call `fetchNextPage`.
          // If there are more records, `page` will get called again.
          // If there are no more records, `done` will get called.
          await sleep(300);
          fetchNextPage();
        },
        function done(err) {
          if (err) {
            console.error(err);
            return;
          }
          let targetEntries = table.filter((entry) => entry[targetField] === targetValue);

          console.log('Retrieved', targetEntries.length, 'records.');
          resolve(targetEntries);
        }
      );
  });
};