import { base } from './airtable_connection';
import { sleep } from './util';


interface Record<T> extends Airtable.Record<T> {
  _rawJson?: {
    createdTime: string;
  };
}


export interface Entry {
  id: string;
  createdTime: string;
  [propName: string]: string | number;
}


export function retrieve(targetSheet: string, targetField: string, targetValue: string): Promise<Entry[]> {
  return new Promise<Entry[]>((resolve, reject) => {
    let table: Entry[] = [];

    base(targetSheet)
      .select({
        view: "Grid view",
        cellFormat: "json"
      })
      .eachPage(
        async function page(records, fetchNextPage) {
          // This function (`page`) will get called for each page of records.
          records.forEach((record: Record<object>) => {
            let entry: Entry = {
              id: record.id,
              createdTime: record._rawJson?.createdTime ?? '',
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

        // @ts-ignore: airtable typing package seems out of date. This finally callback should be valid.
        function done(err: Error) {
          if (err) {
            reject(err);
            return;
          } else if (!(targetField in table[0])) {
            reject(`Column ${targetField} does not exist in ${targetSheet}.`);
            return;
          }
          
          let targetEntries = table.filter((entry: Entry) => entry[targetField] === targetValue);
          console.log('Retrieved', targetEntries.length, 'records.');
          resolve(targetEntries);
        }
      )
  });
};
