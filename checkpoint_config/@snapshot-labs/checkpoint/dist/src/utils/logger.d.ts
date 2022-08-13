import { Logger as PinoLogger, LoggerOptions } from 'pino';
export declare enum LogLevel {
    Silent = "silent",
    Fatal = "fatal",
    Error = "error",
    Warn = "warn",
    Info = "info",
    Debug = "debug"
}
declare type Logger = Omit<PinoLogger, 'trace'>;
export declare const createLogger: (opts?: LoggerOptions) => Logger;
export { Logger, LoggerOptions };
