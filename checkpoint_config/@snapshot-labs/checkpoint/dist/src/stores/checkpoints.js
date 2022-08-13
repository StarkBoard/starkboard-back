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
Object.defineProperty(exports, "__esModule", { value: true });
exports.CheckpointsStore = exports.getCheckpointId = exports.MetadataId = void 0;
const crypto = __importStar(require("crypto"));
const Table = {
    Checkpoints: '_checkpoints',
    Metadata: '_metadatas' // using plural names to confirm with standards entities
};
const Fields = {
    Checkpoints: {
        Id: 'id',
        BlockNumber: 'block_number',
        ContractAddress: 'contract_address'
    },
    Metadata: {
        Id: 'id',
        Value: 'value'
    }
};
/**
 * Metadata Ids stored in the CheckpointStore.
 *
 */
var MetadataId;
(function (MetadataId) {
    MetadataId["LastIndexedBlock"] = "last_indexed_block";
})(MetadataId = exports.MetadataId || (exports.MetadataId = {}));
const CheckpointIdSize = 10;
/**
 * Generates a unique hex based on the contract address and block number.
 * Used when as id for storing checkpoints records.
 *
 */
const getCheckpointId = (contract, block) => {
    const data = `${contract}${block}`;
    return crypto.createHash('sha256').update(data).digest('hex').slice(-CheckpointIdSize);
};
exports.getCheckpointId = getCheckpointId;
/**
 * Checkpoints store is a data store class for managing
 * checkpoints data schema and records.
 *
 * It interacts with an underlying mysql database.
 */
class CheckpointsStore {
    mysql;
    log;
    constructor(mysql, log) {
        this.mysql = mysql;
        this.log = log.child({ component: 'checkpoints_store' });
    }
    /**
     * Creates the core database tables to make Checkpoint run effectively.
     *
     * This only creates the tables if they don't exist.
     */
    async createStore() {
        this.log.debug('creating checkpoints tables...');
        let sql = `CREATE TABLE IF NOT EXISTS ${Table.Checkpoints} (
      ${Fields.Checkpoints.Id} VARCHAR(${CheckpointIdSize}) NOT NULL,
      ${Fields.Checkpoints.BlockNumber} BIGINT NOT NULL,
      ${Fields.Checkpoints.ContractAddress} VARCHAR(66) NOT NULL,
      PRIMARY KEY (${Fields.Checkpoints.Id})
    );`;
        sql += `\nCREATE TABLE IF NOT EXISTS ${Table.Metadata} (
      ${Fields.Metadata.Id} VARCHAR(20) NOT NULL,
      ${Fields.Metadata.Value} VARCHAR(128) NOT NULL,
      PRIMARY KEY (${Fields.Metadata.Id})
    );`;
        await this.mysql.queryAsync(sql);
        this.log.debug('checkpoints tables created');
    }
    async getMetadata(id) {
        const value = await this.mysql.queryAsync(`SELECT ${Fields.Metadata.Value} FROM ${Table.Metadata} WHERE ${Fields.Metadata.Id} = ? LIMIT 1`, [id]);
        if (value.length == 0) {
            return null;
        }
        return value[0][Fields.Metadata.Value];
    }
    async getMetadataNumber(id, base = 10) {
        const strValue = await this.getMetadata(id);
        if (!strValue) {
            return undefined;
        }
        return parseInt(strValue, base);
    }
    async setMetadata(id, value) {
        await this.mysql.queryAsync(`REPLACE INTO ${Table.Metadata} VALUES (?,?)`, [
            id,
            value.toString()
        ]);
    }
    async insertCheckpoints(checkpoints) {
        if (checkpoints.length === 0) {
            return;
        }
        await this.mysql.queryAsync(`INSERT IGNORE INTO ${Table.Checkpoints} VALUES ?`, [
            checkpoints.map(checkpoint => {
                const id = (0, exports.getCheckpointId)(checkpoint.contractAddress, checkpoint.blockNumber);
                return [id, checkpoint.blockNumber, checkpoint.contractAddress];
            })
        ]);
    }
    /**
     * Fetch list of checkpoint blocks greater than or equal to the
     * block number arguments, that have some events related to the
     * contracts in the lists.
     *
     * By default this returns at most 15 next blocks. This return limit
     * can be modified by the limit command.
     */
    async getNextCheckpointBlocks(block, contracts, limit = 15) {
        const result = await this.mysql.queryAsync(`SELECT ${Fields.Checkpoints.BlockNumber} FROM ${Table.Checkpoints} 
      WHERE ${Fields.Checkpoints.BlockNumber} >= ?
        AND ${Fields.Checkpoints.ContractAddress} IN (?)
      ORDER BY ${Fields.Checkpoints.BlockNumber} ASC
      LIMIT ?`, [block, contracts, limit]);
        this.log.debug({ result, block, contracts }, 'next checkpoint blocks');
        return result.map(value => value[Fields.Checkpoints.BlockNumber]);
    }
}
exports.CheckpointsStore = CheckpointsStore;
