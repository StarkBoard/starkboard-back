"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const starknet_1 = require("starknet");
const hash_1 = require("starknet/utils/hash");
const address_1 = require("starknet/utils/address");
const bluebird_1 = __importDefault(require("bluebird"));
const graphql_1 = __importStar(require("./graphql"));
const controller_1 = require("./graphql/controller");
const logger_1 = require("./utils/logger");
const mysql_1 = require("./mysql");
const checkpoint_1 = require("./utils/checkpoint");
const checkpoints_1 = require("./stores/checkpoints");
const graphql_2 = require("graphql");
class Checkpoint {
    config;
    writer;
    schema;
    provider;
    entityController;
    log;
    sourceContracts;
    mysqlPool;
    mysqlConnection;
    checkpointsStore;
    cpBlocksCache;
    constructor(config, writer, schema, opts) {
        this.config = config;
        this.writer = writer;
        this.schema = schema;
        this.entityController = new controller_1.GqlEntityController(schema);
        const providerConfig = this.config.network_base_url
            ? { rpc: { nodeUrl: this.config.network_base_url }}
            : { network: this.config.network };
        this.provider = new starknet_1.Provider(providerConfig);
        this.sourceContracts = (0, checkpoint_1.getContractsFromConfig)(config);
        this.cpBlocksCache = [];
        this.log = (0, logger_1.createLogger)({
            base: { component: 'checkpoint' },
            level: opts?.logLevel || logger_1.LogLevel.Error,
            ...(opts?.prettifyLogs
                ? {
                    transport: {
                        target: 'pino-pretty'
                    }
                }
                : {})
        });
        this.mysqlConnection = opts?.dbConnection;
    }
    /**
     * Returns an express handler that exposes a GraphQL API to query entities defined
     * in the schema.
     *
     */
    get graphql() {
        const entityQueryFields = this.entityController.generateQueryFields();
        const coreQueryFields = this.entityController.generateQueryFields([
            graphql_1.MetadataGraphQLObject,
            graphql_1.CheckpointsGraphQLObject
        ]);
        const querySchema = new graphql_2.GraphQLObjectType({
            name: 'Query',
            fields: {
                ...entityQueryFields,
                ...coreQueryFields
            }
        });
        return (0, graphql_1.default)(querySchema, {
            log: this.log.child({ component: 'resolver' }),
            mysql: this.mysql
        }, this.entityController.generateSampleQuery());
    }
    /**
     * Starts the indexer.
     *
     * The indexer will invoker the respective writer functions when a contract
     * event is found.
     *
     */
    async start() {
        this.log.debug('starting');
        const blockNum = await this.getStartBlockNum();
        return await this.next(blockNum);
    }
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
    async reset() {
        this.log.debug('reset');
        await this.store.createStore();
        await this.store.setMetadata(checkpoints_1.MetadataId.LastIndexedBlock, 0);
        await this.entityController.createEntityStores(this.mysql);
    }
    /**
     * Registers the blocks where a contracts event can be found.
     * This will be used as a skip list for checkpoints while
     * indexing relevant blocks. Using this seed function can significantly
     * reduce the time for Checkpoint to re-index blocks.
     *
     * This should be called before the start() method is called.
     *
     */
    async seedCheckpoints(checkpointBlocks) {
        await this.store.createStore();
        const checkpoints = [];
        checkpointBlocks.forEach(cp => {
            cp.blocks.forEach(blockNumber => {
                checkpoints.push({ blockNumber, contractAddress: cp.contract });
            });
        });
        await this.store.insertCheckpoints(checkpoints);
    }
    async getStartBlockNum() {
        let start = 0;
        let lastBlock = await this.store.getMetadataNumber(checkpoints_1.MetadataId.LastIndexedBlock);
        lastBlock = lastBlock ?? 0;
        const nextBlock = lastBlock + 1;
        if (this.config.tx_fn) {
            if (this.config.start)
                start = this.config.start;
        }
        else {
            (this.config.sources || []).forEach(source => {
                start = start === 0 || start > source.start ? source.start : start;
            });
        }
        return nextBlock > start ? nextBlock : start;
    }
    async next(blockNum) {
        if (!this.config.tx_fn) {
            const checkpointBlock = await this.getNextCheckpointBlock(blockNum);
            if (checkpointBlock)
                blockNum = checkpointBlock;
        }
        this.log.debug({ blockNumber: blockNum }, 'next block');
        let block;
        try {
            block = await this.provider.getBlock(blockNum);
            if (!block.block_number || block.block_number !== blockNum) {
                this.log.error({ blockNumber: blockNum }, 'invalid block');
                await bluebird_1.default.delay(12e3);
                return this.next(blockNum);
            }
        }
        catch (e) {
            if (e.message.includes('StarknetErrorCode.BLOCK_NOT_FOUND')) {
                this.log.info({ blockNumber: blockNum }, 'block not found');
            }
            else {
                this.log.error({ blockNumber: blockNum, err: e }, 'getting block failed... retrying');
            }
            await bluebird_1.default.delay(12e3);
            return this.next(blockNum);
        }
        await this.handleBlock(block);
        await this.store.setMetadata(checkpoints_1.MetadataId.LastIndexedBlock, block.block_number);
        return this.next(blockNum + 1);
    }
    async getNextCheckpointBlock(blockNum) {
        if (this.cpBlocksCache === null) {
            // cache is null when we can no more find a record in the database
            // so exiting early here to avoid polling the database in subsequent
            // loops.
            return null;
        }
        if (this.cpBlocksCache.length !== 0) {
            return this.cpBlocksCache.shift();
        }
        const checkpointBlocks = await this.store.getNextCheckpointBlocks(blockNum, this.sourceContracts);
        if (checkpointBlocks.length === 0) {
            this.log.info({ blockNumber: blockNum }, 'no more checkpoint blocks in store');
            // disabling cache to stop polling database
            this.cpBlocksCache = null;
            return null;
        }
        this.cpBlocksCache = checkpointBlocks;
        return this.cpBlocksCache.shift();
    }
    async handleBlock(block) {
        this.log.info({ blockNumber: block.block_number }, 'handling block');
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore
        for (const receipt of block.transaction_receipts || []) {
            await this.handleTx(block, block.transactions[receipt.transaction_index], receipt);
        }
        this.log.debug({ blockNumber: block.block_number }, 'handling block done');
    }
    async handleTx(block, tx, receipt) {
        this.log.debug({ txIndex: tx.transaction_index }, 'handling transaction');
        if (this.config.tx_fn)
            await this.writer[this.config.tx_fn]({ block, tx, receipt, mysql: this.mysql });
        for (const source of this.config.sources || []) {
            let foundContractData = false;
            const contract = (0, address_1.validateAndParseAddress)(source.contract);
            if (tx.type === 'DEPLOY' &&
                source.deploy_fn &&
                contract === (0, address_1.validateAndParseAddress)(tx.contract_address)) {
                foundContractData = true;
                this.log.info({ contract: source.contract, txType: tx.type, handlerFn: source.deploy_fn }, 'found deployment transaction');
                await this.writer[source.deploy_fn]({ source, block, tx, receipt, mysql: this.mysql });
            }
            for (const event of receipt.events) {
                if (contract === (0, address_1.validateAndParseAddress)(event.from_address)) {
                    for (const sourceEvent of source.events) {
                        if (`0x${(0, hash_1.starknetKeccak)(sourceEvent.name).toString('hex')}` === event.keys[0]) {
                            foundContractData = true;
                            this.log.info({ contract: source.contract, event: sourceEvent.name, handlerFn: sourceEvent.fn }, 'found contract event');
                            await this.writer[sourceEvent.fn]({
                                source,
                                block,
                                tx,
                                receipt,
                                event,
                                mysql: this.mysql
                            });
                        }
                    }
                }
            }
            if (foundContractData) {
                await this.store.insertCheckpoints([
                    { blockNumber: block.block_number, contractAddress: source.contract }
                ]);
            }
        }
        this.log.debug({ txIndex: tx.transaction_index }, 'handling transaction done');
    }
    get store() {
        if (this.checkpointsStore) {
            return this.checkpointsStore;
        }
        return (this.checkpointsStore = new checkpoints_1.CheckpointsStore(this.mysql, this.log));
    }
    get mysql() {
        if (this.mysqlPool) {
            return this.mysqlPool;
        }
        // lazy initialization of mysql connection
        return (this.mysqlPool = (0, mysql_1.createMySqlPool)(this.mysqlConnection));
    }
}
exports.default = Checkpoint;
