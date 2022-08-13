import { toAddress, dateFormat } from './utils';
import { toBN, fromWei } from 'web3-utils';
import { transferTableName, bridgeTableName } from './config.json';
import config from './config.json';
import bothNetTokens from '../tokens.json';

let tokens;
if (config.network === 'goerli-alpha') {
	tokens = bothNetTokens.goerli;
}
else if (config.network === 'mainnet-alpha') {
	tokens = bothNetTokens.mainnet;
}
else {
	throw new Error(`Unknown network: "${config.network}" - should be "mainnet-alpha" or "goerli-alpha"`);
}

export async function handleTransfer({ tx, block, receipt, event, mysql }) {

	let i = 0;
	let tokenSymbol = "";
	while (i < tokens.length) {
		if (toBN(event.from_address).eq(toBN(tokens[i].l2_token_address))) {
			{
				tokenSymbol = tokens[i].symbol;
				break;
			}
		}
		i++;
	}

	const author = toAddress(event.data[0]);
	const recipient = toAddress(event.data[1]);
	const value = fromWei(toBN(event.data[2]));
	const txHash = receipt.transaction_hash;
	const timestamp = block.timestamp;
	const blockNumber = block.block_number;
	const { fullDay, time } = dateFormat(timestamp);
	let id : String;
	if (txHash.indexOf("0x") !== -1) {
		id = `${blockNumber}/${txHash.split("x")[1]}`;
	}
	else {
		id = `${blockNumber}/${txHash}`;
	}

	if (author === '0x0') {
		const deposit = {
			id,
			token: tokenSymbol,
			type: "deposit",
			value,
			tx_hash: txHash,
			fullDay,
			time,
			created_at_block: blockNumber
		}
	
		await mysql.queryAsync(`INSERT IGNORE INTO ${bridgeTableName} SET ?`, [deposit]);
	}
	else if (recipient === '0x0') {
		const withdrawal = {
			id,
			token: tokenSymbol,
			type: "witdhrawal",
			value,
			tx_hash: txHash,
			fullDay,
			time,
			created_at_block: blockNumber
		}
	
		await mysql.queryAsync(`INSERT IGNORE INTO ${bridgeTableName} SET ?`, [withdrawal]);
	}
	else {
		const transfer = {
			id,
			token: tokenSymbol,
			author,
			value,
			tx_hash: txHash,
			fullDay,
			time,
			created_at_block: blockNumber
		};

		await mysql.queryAsync(`INSERT IGNORE INTO ${transferTableName} SET ?`, [transfer]);
	}
}
