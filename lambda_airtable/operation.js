const { sleepPromise, filterUndefined } = require('./util');


exports.retrieve = function(params) {
  /*
  Params = {
    base, sheet, processRecord, filterRecord,
    view, cellFormat, maxRecords, fields, sort, filterRecordByFormula
  }
  Parameters other than `base` and `sheet` are optional
  */
  let { base, sheet, processRecord, filterRecord } = params;

  function constructAirParams({
    view='Grid view', cellFormat="json",
    maxRecords, fields, sort, filterRecordByFormula
  }) {
    return filterUndefined({
      view, maxRecords, fields, sort, cellFormat,
      filterByFormula: filterRecordByFormula,
    });
  }
  const airParams = constructAirParams(params);

  return new Promise((resolve, reject) => {
    let table = [];
    base(sheet)
      .select(airParams)
      .eachPage(  // Record per page = 100
        async function page(records, fetchNextPage) {
          // This function (`page`) will get called for each page of records.
          
          // Make the records into a proper format
          records.forEach((record) => table.push(processRecord(record)));
    
          // To fetch the next page of records, call `fetchNextPage`.
          // If there are more records, `page` will get called again.
          // If there are no more records, `done` will get called.
          await sleepPromise(200);
          fetchNextPage();
        },
        function done(err) {
          if (err) {
            console.error(err);
            reject();
          }
          
          // Additional filter by js
          const targetEntries = filterRecord ? table.filter(filterRecord) : table;

          console.log('Retrieved', targetEntries.length, 'records.');
          resolve(targetEntries);
        }
      );
  });
};


exports.retrieveReduce = async function(params) {
  /*
  Params = {
    base, sheet, processRecord, filterRecord, reduceRecord, reduceDefault,
    view, cellFormat, maxRecords, fields, sort, filterRecordByFormula
  }
  Parameters other than `base` and `sheet` are optional
  */
  const { reduceRecord, reduceDefault } = params;

  const targetEntries = await exports.retrieve(params);

  const reducedOutput = targetEntries.reduce(reduceRecord, reduceDefault);
  console.log('Reduced records.')
  return reducedOutput
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


exports.find = function(params) {
  /*
  Find by record Iid, which is the internal record ID and is hidden from the Airtable frontend.
  */
  let { base, sheet, recordId } = params;

  return new Promise((resolve, reject) => {
    base(sheet).find(recordId, (err, record) => {
      if (err) {
        console.error(err);
        reject();
      }
      console.log(`Found record, ${record.id}.`);
      resolve(record);
    });
  });
};


exports.update = function(params) {
  /*
  Find by record Iid, and update the specified fields.
  Example `entries` = [{
    "id": recordIid,
    "fields": {
      "完成": true,
    }
  }]
  */
  let { base, sheet, entries } = params;

  return new Promise((resolve, reject) => {
    console.log(entries)
    base(sheet).update(entries, (err, records) => {
      if (err) {
        console.error(err);
        reject();
      }
      records.forEach((record) => {
        console.log(`Updated ${record.id} in ${sheet}.`);
      });
      resolve();
    });
  });
};