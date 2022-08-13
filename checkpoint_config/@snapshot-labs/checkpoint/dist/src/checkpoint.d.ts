/// <reference types="node" />
import { Provider } from 'starknet';
import Promise from 'bluebird';
import { CheckpointConfig, CheckpointOptions, CheckpointWriters } from './types';
export default class Checkpoint {
    config: CheckpointConfig;
    writer: CheckpointWriters;
    schema: string;
    provider: Provider;
    private readonly entityController;
    private readonly log;
    private readonly sourceContracts;
    private mysqlPool?;
    private mysqlConnection?;
    private checkpointsStore?;
    private cpBlocksCache;
    constructor(config: CheckpointConfig, writer: CheckpointWriters, schema: string, opts?: CheckpointOptions);
    /**
     * Returns an express handler that exposes a GraphQL API to query entities defined
     * in the schema.
     *
     */
    get graphql(): (request: import("http").IncomingMessage & {
        url: string;
    }, response: import("http").ServerResponse & {
        json?: ((data: unknown) => void) | undefined;
    }) => Promise<void>;
    /**
     * Starts the indexer.
     *
     * The indexer will invoker the respective writer functions when a contract
     * event is found.
     *
     */
    start(): Promise<any>;
    /**
     * Reset will clear the last synced block informations
     * and force Checkpoint to start indexing from the start
     * block.
     *
     * This will also clear all indexed GraphQL entity records.
     *
     * This should be called when there has been a change to the GraphQL schema
     * or a change to the writer functions logic, so indexing will re-run from
     * the starting block. Also, it should be called the first time Checkpoint
     * is being initialized.
     *
     */
    reset(): Promise<void>;
    /**
     * Registers the blocks where a contracts event can be found.
     * This will be used as a skip list for checkpoints while
     * indexing relevant blocks. Using this seed function can significantly
     * reduce the time for Checkpoint to re-index blocks.
     *
     * This should be called before the start() method is called.
     *
     */
    seedCheckpoints(checkpointBlocks: {
        contract: string;
        blocks: number[];
    }[]): Promise<void>;
    private getStartBlockNum;
    private next;
    private getNextCheckpointBlock;
    private handleBlock;
    private handleTx;
    private get store();
    private get mysql();
}
