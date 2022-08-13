"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.createMySqlPool = void 0;
const mysql_1 = __importDefault(require("mysql"));
const Pool_1 = __importDefault(require("mysql/lib/Pool"));
const Connection_1 = __importDefault(require("mysql/lib/Connection"));
const bluebird_1 = __importDefault(require("bluebird"));
const connection_string_1 = require("connection-string");
bluebird_1.default.promisifyAll([Pool_1.default, Connection_1.default]);
/**
 * Attempts to connect to the database by the connection string. If no connection string
 * argument is provided, it tries to use the `DATABASE_URL` environment variable
 * as connection string.
 *
 * This returns a mysql pool connection object.
 */
const createMySqlPool = (connection) => {
    if (!connection && !process.env.DATABASE_URL) {
        throw new Error('a valid connection string or DATABASE_URL environment variable is required to connect to the database');
    }
    const connectionConfig = new connection_string_1.ConnectionString((connection || process.env.DATABASE_URL));
    if (!connectionConfig.hosts || !connectionConfig.path) {
        throw new Error('invalid mysql connection string provided');
    }
    const config = {
        connectionLimit: 1,
        multipleStatements: true,
        database: connectionConfig.path[0],
        user: connectionConfig.user,
        password: connectionConfig.password,
        host: connectionConfig.hosts[0].name,
        port: connectionConfig.hosts[0].port,
        connectTimeout: 30000,
        charset: 'utf8mb4'
    };
    return mysql_1.default.createPool(config);
};
exports.createMySqlPool = createMySqlPool;
