"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getContractsFromConfig = void 0;
const getContractsFromConfig = (config) => {
    return (config.sources || []).map(source => source.contract);
};
exports.getContractsFromConfig = getContractsFromConfig;
