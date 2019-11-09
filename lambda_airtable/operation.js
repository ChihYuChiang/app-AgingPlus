const { sleepPromise } = require('./util');


exports.retrieve = function(params) {
  let { base, sheet, processRecord, filterRecord } = params;

  return new Promise((resolve, reject) => {
    let table = [];
    base(sheet)
      .select({
        view: "Grid view",
        cellFormat: "json"
      })
      .eachPage(
        async function page(records, fetchNextPage) {
          //This function (`page`) will get called for each page of records.
    
          records.forEach((record) => {
            let entry = processRecord(record);
            table.push(entry);
          });
    
          //To fetch the next page of records, call `fetchNextPage`.
          //If there are more records, `page` will get called again.
          //If there are no more records, `done` will get called.
          await sleepPromise(300);
          fetchNextPage();
        },
        function done(err) {
          if (err) {
            console.error(err);
            reject();
          }
          
          let targetEntries = table.filter(filterRecord);
          console.log('Retrieved', targetEntries.length, 'records.');
          resolve(targetEntries);
        }
      );
  });
};

exports.create = function(params) {
  /*
  Example `entries` = [{
    "fields": {
      "LineUserId": lineUserId,
      "LineDisplayName": lineDisplayName,
      "LineProfilePicture": lineProfilePic
    }
  }]
  */
  let { base, sheet, entries } = params;

  return new Promise((resolve, reject) => {
    base(sheet).create(entries, (err, records) => {
      if (err) {
        console.error(err);
        reject();
      }
      records.forEach((record) => {
        console.log(`Added ${JSON.stringify(record.fields)} to ${sheet} record.`);
      });
      resolve();
    });
  });
};