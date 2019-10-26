const Airtable = require("airtable");
const moment = require('moment');
const { sleep } = require('./util');

const base = new Airtable({ apiKey: process.env.AIRTABLE_APIKEY }).base(process.env.BASE_ID);
const AIR_EVENT_TYPES = {
  FOLLOW: 'follow',
  REMINDER: 'reminder'
};

function handlerBuilder(...funcs) {
  return (event, context) => {
    for(let func of funcs) { func(event); }
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
  return { statusCode: 200, body: 'OK' };
};

async function handle_reminder(event) {
  if(event.eventType !== AIR_EVENT_TYPES.REMINDER) { return }

  const idTargets = () => {
    return new Promise((resolve, reject) => {
      let table = [];
      base('LINE-MEMBER')
        .select({
          view: "Grid view",
          cellFormat: "json"
        })
        .eachPage(
          async function page(records, fetchNextPage) {
            //This function (`page`) will get called for each page of records.
      
            records.forEach((record) => {
              let entry = {
                  "id": record.id,
                  "lineUserId": record.fields.LineUserId,
                  "messageTime": moment(record.fields.MessageTime),
                  "messageContent": record.fields.MessageContent
              };
              table.push(entry);
            });
      
            //To fetch the next page of records, call `fetchNextPage`.
            //If there are more records, `page` will get called again.
            //If there are no more records, `done` will get called.
            await sleep(300);
            fetchNextPage();
          },
          function done(err) {
            if (err) {
              console.error(err);
              return;
            }
            //If the scheduled message time is tomorrow
            let targetEntries = table.filter((entry) => {
              return moment().add(1, 'days').isSame(entry.messageTime, 'day')
            });
  
            console.log('Retrieved', targetEntries.length, 'records.');
            resolve(targetEntries);
          }
        );
    });
  };

  const targets = await idTargets();
  console.log(targets)
  //TODO: invoke LINE lambda here

  return { statusCode: 200, body: 'OK' };
};


exports.handler = handlerBuilder(
  handle_follow,
  handle_reminder
);