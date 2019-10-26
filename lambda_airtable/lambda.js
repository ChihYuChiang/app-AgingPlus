const Airtable = require("airtable");

const base = new Airtable({ apiKey: process.env.AIRTABLE_APIKEY }).base(process.env.BASE_ID);
const AIR_EVENT_TYPES = {
  FOLLOW: 'follow'
};

function handlerBuilder(...funcs) {
  return (event, context) => {
    for(let func of funcs) { func(event); }
  };
}


async function handle_follow(jsonBody) {
  if(jsonBody.eventType !== AIR_EVENT_TYPES.FOLLOW) { return }

  const lineUserId = jsonBody.lineUserId;
  const lineDisplayName = jsonBody.lineDisplayName;

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


exports.handler = handlerBuilder(
  handle_follow
);