import { AsyncMySqlPool } from '../mysql';
import { Logger } from '../utils/logger';
declare type ToString = {
    toString: () => string;
};
export interface CheckpointRecord {
    blockNumber: number;
    contractAddress: string;
}
/**
 * Metadata Ids stored in the CheckpointStore.
 *
 */
export declare enum MetadataId {
    LastIndexedBlock = "last_indexed_block"
}
/**
 * Generates a unique hex based on the contract address and block number.
 * Used when as id for storing checkpoints records.
 *
 */
export declare const getCheckpointId: (contract: string, block: number) => string;
/**
 * Checkpoints store is a data store class for managing
 * checkpoints data schema and records.
 *
 * It interacts with an underlying mysql database.
 */
export declare class CheckpointsStore {
    private readonly mysql;
    private readonly log;
    constructor(mysql: AsyncMySqlPool, log: Logger);
    /**
     * Creates the core database tables to make Checkpoint run effectively.
     *
     * This only creates the tables if they don't exist.
     */
    createStore(): Promise<void>;
    getMetadata(id: string): Promise<string | null>;
    getMetadataNumber(id: string, base?: number): Promise<number | undefined>;
    setMetadata(id: string, value: ToString): Promise<void>;
    insertCheckpoints(checkpoints: CheckpointRecord[]): Promise<void>;
    /**
     * Fetch list of checkpoint blocks greater than or equal to the
     * block number arguments, that have some events related to the
     * contracts in the lists.
     *
     * By default this returns at most 15 next blocks. This return limit
     * can be modified by the limit command.
     */
    getNextCheckpointBlocks(block: number, contracts: string[], limit?: number): Promise<number[]>;
}
export {};
