const fs = require("fs");
const yaml = require('js-yaml');
const { Parser } = require("json2csv");
const Airtable = require("airtable");

const cred = yaml.safeLoad(fs.readFileSync('./ref/credential.yml', 'utf8'));
const base = new Airtable({ apiKey: cred.Airtable.apiKey }).base(cred.Airtable.baseId);

var table = [];
base("基本菜單")
  .select({
    // Selecting the first 3 records in Grid view:
    maxRecords: 3,
    view: "Grid view",
    cellFormat: "json"
  })
  .eachPage(
    function page(records, fetchNextPage) {
      // This function (`page`) will get called for each page of records.

      records.forEach(function(record) {
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
      fetchNextPage();
    },
    function done(err) {
      if (err) {
        console.error(err);
        return;
      }
      const fields = Object.keys(table[0]);
      const json2csvParser = new Parser({ fields });
      const tableCsv = json2csvParser.parse(table);

      fs.writeFile("./data/output.csv", tableCsv, "utf8", function(err) {
        if (err) {
          console.log("An error occurred while writing the Object to File.");
          return console.log(err);
        }

        console.log("CSV file has been saved.");
      });
    }
  );
