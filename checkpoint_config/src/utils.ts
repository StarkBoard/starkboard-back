import { getAddress } from '@ethersproject/address';
import { BigNumber } from '@ethersproject/bignumber';
import mysql from 'mysql';
import config from './config.json'


export const toAddress = bn => {
	try {
		return getAddress(BigNumber.from(bn).toHexString());
	} catch (e) {
		return bn;
	}
};

export const dateFormat = timestamp => {
	const date = new Date(timestamp * 1000);
	
	const month = date.getUTCMonth() + 1;
	const day = date.getUTCDate();
	const year = date.getUTCFullYear();
	const hour = date.getUTCHours();
	const minute = date.getUTCMinutes();
	const second = date.getUTCSeconds();

	return {
			fullDay: `${year}-${month}-${day}`,
			time: `${hour}:${minute}:${second}`
	};
};

export const checkpointSourceTransfer = (address: string, startingBlock: number) => {
	return {
		contract: address,
		start: startingBlock,
		events: [
			{
				name: "Transfer",
				fn: "handleTransfer"
			}
		]
	}
}

export const createTablesIfMissing = () => {
	const connection = mysql.createConnection(process.env.DATABASE_URL);
	connection.connect((error) => {
		if (error) {
			throw new Error(error);
		}
		connection.query(`CREATE TABLE ${config.transferTableName} (
			id VARCHAR(255) NOT NULL PRIMARY KEY,
			token VARCHAR(255) NOT NULL,
			author VARCHAR(255),
			value FLOAT,
			tx_hash VARCHAR(255) NOT NULL,
			fullDay VARCHAR(255) NOT NULL,
			time VARCHAR(255) NOT NULL,
			created_at_block INTEGER
		)`,
		(error, results) => {
		});
		connection.query(`CREATE TABLE ${config.bridgeTableName} (
			id VARCHAR(255) NOT NULL PRIMARY KEY,
			token VARCHAR(255) NOT NULL,
			type VARCHAR(255) NOT NULL,
			value FLOAT,
			tx_hash	VARCHAR(255) NOT NULL,
			fullDay VARCHAR(255) NOT NULL,
			time VARCHAR(255) NOT NULL,
			created_at_block INTEGER
		)`,
		(error, results) => {
		});
		connection.end();
	});
}