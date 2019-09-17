const fs = require("fs");
const { Parser } = require("json2csv");
const { retrieve } = require('./airtable_retrieve.js');

retrieve('Table 9', 'Name', 'test').then((retrievedEntries) => {
  const fields = Object.keys(retrievedEntries[0]);
  const json2csvParser = new Parser({ fields });
  const table = json2csvParser.parse(retrievedEntries);

  fs.writeFile("./data/output.csv", table, "utf8", function(err) {
    if (err) {
      console.log("An error occurred while writing the Object to File.");
      return console.log(err);
    }

    console.log("CSV file has been saved.");
  });
});