import 'dotenv/config';
import path from 'path';
import fs from 'fs';
import Checkpoint, { LogLevel } from '@snapshot-labs/checkpoint';
import config from './config.json';
import * as writers from './writers';
import { checkpointSourceTransfer, createTablesIfMissing } from './utils';
import bothNetTokens from '../tokens.json';

let tokens;
if (config.network === 'goerli-alpha') {
	tokens = bothNetTokens.goerli;
}
else if (config.network === 'mainnet-alpha') {
	tokens = bothNetTokens.mainnet;
}
for (const token of config.tokens) {
	let i = 0;
	while (i < tokens.length) {
		if (token === tokens[i].symbol)
			break;
		i++;
	}
	if (i === tokens.length) {
		throw new Error(`Unknown token: "${token}" - should be one of JSON tokens file`);
	}
}

const dir = __dirname.endsWith('dist/src') ? '../' : '';
const schemaFile = path.join(__dirname, `${dir}../src/schema.gql`);
const schema = fs.readFileSync(schemaFile, 'utf8');
const checkpointOptions = {
  logLevel: LogLevel.Info
};
let checkpointConfig = {
	network: config.network,
	sources: new Array
};

for (const tokenSymbol of config.tokens) {
	let i = 0;
	while (i < tokens.length) {
		if (tokenSymbol === tokens[i].symbol)
			break;
		i++;
	}
	checkpointConfig.sources.push(checkpointSourceTransfer(tokens[i].l2_token_address, config.startingBlock));
}

//createTablesIfMissing();
// @ts-ignore
const checkpoint = new Checkpoint(checkpointConfig, writers, schema, checkpointOptions);
checkpoint.start();
