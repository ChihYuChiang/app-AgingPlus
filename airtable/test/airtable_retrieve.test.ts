// @ts-nocheck
import * as fs from 'fs';
import * as yaml from 'js-yaml';
import Airtable from 'airtable';
import { base } from '../src/airtable_connection';
import { retrieve } from '../src/airtable_retrieve';

const cred = yaml.safeLoad(fs.readFileSync('../ref/credential.yml', 'utf8'));
const base_test = new Airtable({ apiKey: cred.Airtable_Test.apiKey }).base(cred.Airtable_Test.baseId);

jest.mock('../src/airtable_connection');
base.mockImplementation(base_test);


test('base with good credential', (done) => {
  try {
    base('test_airtable')
      .select({
        view: "Grid view",
        cellFormat: "json"
      })
      .eachPage((records, fetchNextPage) => {
        expect(records.length).toBe(3)
        done();
      });
  } catch (err) {
    done(err);
  }
});
 
test('retrieve normal', () => {
  return expect(retrieve('test_airtable', 'Status', 'Done')).resolves.toHaveLength(2);
});

test('retrieve wrong table', () => {
  return expect(retrieve('bad_table', 'Status', 'Done')).rejects.toHaveProperty('error', 'NOT_FOUND');
});

test('retrieve wrong column', async () => {
  return expect(retrieve('test_airtable', 'bad_col', 'Done')).rejects.toMatch('does not exist in');
});
