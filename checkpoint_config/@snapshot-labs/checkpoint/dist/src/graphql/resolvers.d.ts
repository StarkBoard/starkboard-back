import { AsyncMySqlPool } from '../mysql';
import { Logger } from '../utils/logger';
/**
 *
 */
export interface ResolverContext {
    log: Logger;
    mysql: AsyncMySqlPool;
}
export declare function queryMulti(parent: any, args: any, context: ResolverContext, info: any): Promise<any>;
export declare function querySingle(parent: any, args: any, context: ResolverContext, info: any): Promise<any>;
