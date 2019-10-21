const Airtable = require("airtable");

const base = new Airtable({ apiKey: process.env.AIRTABLE_APIKEY }).base(process.env.BASE_ID);

base('LINE-MEMBER').create([
  {
    "fields": {
      "LineUserId": "hello",
      "LineDisplayName": "CY"
    }
  }
], function(err, records) {
  if (err) {
    console.error(err);
    return;
  }
  records.forEach((record) => {
    console.log('Added ' + record.fields.LineDisplayName + ' to Line member record.');
  });
});