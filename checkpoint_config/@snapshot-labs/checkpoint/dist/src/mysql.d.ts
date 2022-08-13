import { Pool as PoolType, QueryOptions } from 'mysql';
/**
 * Type definition for the promisified Pool type.
 *
 * This has to be updated manually with new promisified methods
 * that users will like to access.
 */
export interface AsyncMySqlPool extends PoolType {
    queryAsync: (options: string | QueryOptions, values?: any) => Promise<any>;
}
/**
 * Attempts to connect to the database by the connection string. If no connection string
 * argument is provided, it tries to use the `DATABASE_URL` environment variable
 * as connection string.
 *
 * This returns a mysql pool connection object.
 */
export declare const createMySqlPool: (connection?: string) => AsyncMySqlPool;
