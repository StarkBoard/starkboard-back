import { Transaction, TransactionReceipt, GetBlockResponse } from 'starknet';
import { AsyncMySqlPool } from './mysql';
import { LogLevel } from './utils/logger';
export interface CheckpointOptions {
    logLevel?: LogLevel;
    prettifyLogs?: boolean;
    dbConnection?: string;
}
export interface ContractEventConfig {
    name: string;
    fn: string;
}
export interface ContractSourceConfig {
    contract: string;
    start: number;
    deploy_fn?: string;
    events: ContractEventConfig[];
}
export interface CheckpointConfig {
    network?: SupportedNetworkName | string;
    network_base_url?: string;
    start?: number;
    tx_fn?: string;
    sources?: ContractSourceConfig[];
}
export declare type SupportedNetworkName = 'mainnet-alpha' | 'goerli-alpha';
/**
 * Callback function invoked by checkpoint when a contract event
 * is encountered. A writer function should use the `mysql`
 * object to write to the database entities based on the require logic.
 *
 * For example, if a graphql Entity is defined in the schema:
 *
 * ```graphql
 * type Vote {
 *  id: ID!
 *  voter: String!
 * }
 * ```
 *
 * Then you can insert into the entity into the database like:
 * ```typescript
 * await args.mysql.queryAsync('INSERT INTO votes VALUES(?, ?);', ['voteId', 'voters-address']);
 * ```
 *
 * Note, Graphql Entity names are lowercased with an 's' suffix when
 * interacting with them in the databas.
 *e
 */
export declare type CheckpointWriter = (args: {
    tx: Transaction;
    block: GetBlockResponse;
    receipt: TransactionReceipt;
    event?: Array<any>;
    source?: ContractSourceConfig;
    mysql: AsyncMySqlPool;
}) => Promise<void>;
/**
 * Object map of events to CheckpointWriters.
 *
 * The CheckpointWriter function will be invoked when an
 * event matching a key is found.
 *
 */
export interface CheckpointWriters {
    [event: string]: CheckpointWriter;
}
