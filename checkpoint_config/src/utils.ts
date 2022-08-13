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
	let connection = mysql.createConnection(process.env.DATABASE_URL);
	connection.connect((error) => {
		if (error) {
			connection.end();
			throw new Error(error);
		}
		connection.query(`CREATE TABLE ${config.transferTableName} (
			id STRING PRIMARY KEY,
			token STRING,
			author STRING,
			value FLOAT,
			tx_hash STRING
			fullDay STRING,
			time STRING,
			created_at_block INTEGER
		)`,
		(error, results) => {
			if (error) {
				connection.end();
				throw new Error(error);
			}
		});
		connection.query(`CREATE TABLE ${config.transferTableName} (
			id STRING PRIMARY KEY,
			token STRING,
			type STRING,
			value FLOAT,
			tx_hash	STRING,
			fullDay STRING,
			time STRING,
			created_at_block INTEGER
		)`,
		(error, results) => {
			if (error) {
				connection.end();
				throw new Error(error);
			}
		});
		connection.end();
	});
}