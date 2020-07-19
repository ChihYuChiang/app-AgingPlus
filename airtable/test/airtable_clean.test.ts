// @ts-nocheck
import * as fs from 'fs';
import * as yaml from 'js-yaml';
import Airtable from 'airtable';
import { base } from '../src/airtable_connection';
import { clean } from '../src/airtable_clean';
import { retrieve } from '../src/airtable_retrieve';

jest.setTimeout(15000);  // 15 secs 

const cred = yaml.safeLoad(fs.readFileSync('../ref/credential.yml', 'utf8'));
const base_test = new Airtable({ apiKey: cred.Airtable_Test.apiKey }).base(cred.Airtable_Test.baseId);

jest.mock('../src/airtable_connection');
base.mockImplementation(base_test);

afterAll(() => {
  base_test('test_airtable').create([
    {
      "fields": {
        "Name": "test1",
        "Status": "Done"
      }
    },
    {
      "fields": {
        "Name": "test2",
        "Status": "Done"
      }
    }
  ], function(err, records) {
    if (err) {
      console.error(err);
      return;
    }
  });
});


test('clean sheet content', async () => {
  await clean('test_airtable', 'Status', 'Done');

  await expect(retrieve('test_airtable', 'Status', 'Done')).resolves.toHaveLength(0);
});
