// @ts-nocheck
import * as fs from 'fs';
import * as yaml from 'js-yaml';
import csv from 'jquery-csv';
import Airtable from 'airtable';
import { base } from '../src/airtable_connection';
import { dump } from '../src/airtable_dump';

const cred = yaml.safeLoad(fs.readFileSync('../ref/credential.yml', 'utf8'));
const base_test = new Airtable({ apiKey: cred.Airtable_Test.apiKey }).base(cred.Airtable_Test.baseId);

jest.mock('../src/airtable_connection');
base.mockImplementation(base_test);


test('dump to file', async () => {
  await dump('test_airtable', 'Status', 'Done');

  let data = fs.readFileSync('./data/output.csv', 'utf8');
  data = csv.toObjects(data);

  expect(data.length).toBe(2);
});
