const Airtable = require("airtable");
const moment = require('moment');
const { sleepPromise, filterUndefined } = require('./util');

const base = new Airtable({ apiKey: process.env.AIRTABLE_APIKEY }).base(process.env.BASE_ID);
const AIR_EVENT_TYPES = {
  FOLLOW: 'follow',
  REMINDER: 'reminder',
  NEXT_CLASS: 'next_class' //TODO: next class
};

function handlerBuilder(...funcs) {
  return async (event, context) => {
    //Concurrent fire all handlers
    let promises = funcs.map((func) => func(event));
    let results = filterUndefined(await Promise.all(promises));

    //Res with an array with all activated handlers
    console.log(results)
    return results;
  };
}


async function handle_follow(event) {
  if(event.eventType !== AIR_EVENT_TYPES.FOLLOW) { return }

  const lineUserId = event.lineUserId;
  const lineDisplayName = event.lineDisplayName;

  const createMember = () => {
    return new Promise((resolve, reject) => {
      base('LINE-MEMBER').create([
        {
          "fields": {
            "LineUserId": lineUserId,
            "LineDisplayName": lineDisplayName
          }
        }
      ], (err, records) => {
        if (err) {
          console.error(err);
          reject();
        }
        records.forEach((record) => {
          console.log('Added ' + record.fields.LineDisplayName + ' to Line member record.');
        });
        resolve();
      });
    });
  };

  await createMember();
  return { Status: 'handle_follow: OK' };
};

async function handle_reminder(event) {
  if(event.eventType !== AIR_EVENT_TYPES.REMINDER) { return }

  const params = {
    baseName: 'LINE-MEMBER',
    processRecord: (record) => ({
      "id": record.id,
      "lineUserId": record.fields.LineUserId,
      "lineDisplayName": record.fields.LineDisplayName,
      "messageTime": moment(record.fields.MessageTime),
      "messageContent": record.fields.MessageContent    
    }),
    //If the scheduled message time is tomorrow
    filterRecord: (record) => moment().add(1, 'days').isSame(record.messageTime, 'day')
  }
  
  const targets = await retrieve(params);
  return { Status: 'handle_reminder: OK', Data: targets };
};


exports.handler = handlerBuilder(
  handle_follow,
  handle_reminder
);


//TODO: move the generalization to operation
function retrieve(params) {
  let { baseName, processRecord, filterRecord } = params;

  return new Promise((resolve, reject) => {
    let table = [];
    base(baseName)
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