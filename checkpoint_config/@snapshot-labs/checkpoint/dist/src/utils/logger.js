"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.createLogger = exports.LogLevel = void 0;
const pino_1 = __importDefault(require("pino"));
// LogLevel to control what levels of logs are
// required.
var LogLevel;
(function (LogLevel) {
    // silent to disable all logging
    LogLevel["Silent"] = "silent";
    // fatal to log unrecoverable errors
    LogLevel["Fatal"] = "fatal";
    // error to log general errors
    LogLevel["Error"] = "error";
    // warn to log alerts or notices
    LogLevel["Warn"] = "warn";
    // info to log useful information
    LogLevel["Info"] = "info";
    // debug to log debug and trace information
    LogLevel["Debug"] = "debug";
})(LogLevel = exports.LogLevel || (exports.LogLevel = {}));
const createLogger = (opts = {}) => {
    return (0, pino_1.default)(opts, pino_1.default.destination({
        sync: true
    }));
};
exports.createLogger = createLogger;
