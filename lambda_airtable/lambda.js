const Airtable = require("airtable");
const moment = require('moment');
const { retrieve, create } = require('./operation.js');
const { filterUndefined } = require('./util');

const base = new Airtable({ apiKey: process.env.AIRTABLE_APIKEY }).base(process.env.BASE_ID);
const AIR_EVENT_TYPES = {
  FOLLOW: 'follow',
  REMINDER: 'reminder',
  NEXT_CLASS: 'next_class'
};

//TODO: remove the awkward list results
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
  if(event.eventType !== AIR_EVENT_TYPES.FOLLOW) { return; }

  const { lineUserId, lineDisplayName, lineProfilePic } = event;
  const params = {
    base: base,
    sheet: 'LINE-MEMBER',
    entries: [
      {
        "fields": {
          "LineUserId": lineUserId,
          "LineDisplayName": lineDisplayName,
          "LineProfilePicture": lineProfilePic
        }
      }
    ]
  };

  //TODO: handle reject error
  await create(params);
  return { Status: 'handle_follow: OK' };
};

async function handle_reminder(event) {
  if(event.eventType !== AIR_EVENT_TYPES.REMINDER) { return; }

  const params = {
    base: base,
    sheet: 'LINE-MEMBER',
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

async function handle_nextClass(event) {
  if(event.eventType !== AIR_EVENT_TYPES.NEXT_CLASS) { return; }

  //Use Line ID get aging member id

  //Use aging member id get next class info
};


exports.handler = handlerBuilder(
  handle_follow,
  handle_reminder,
  handle_nextClass
);