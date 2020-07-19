// @ts-nocheck
import { base } from '../src/airtable_connection';


test('base set up connection query', () => {
  const query = base('test_table')
    .select({
      view: 'Grid view',
      cellFormat: 'json'
    });

  expect(query._params.view).toBe('Grid view');
  expect(query._table.name).toBe('test_table');
});
