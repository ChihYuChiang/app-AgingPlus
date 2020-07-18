import * as fs from 'fs';
import * as yaml from 'js-yaml';
import Airtable from 'airtable';


interface Cred {
  readonly Airtable: {
    readonly apiKey: string;
    readonly baseId: string;
  };
}

const cred = yaml.safeLoad(fs.readFileSync('../ref/credential.yml', 'utf8')) as Cred;


export const base = new Airtable({ apiKey: cred.Airtable.apiKey }).base(cred.Airtable.baseId);
