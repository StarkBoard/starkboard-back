"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.generateQueryForEntity = exports.multiEntityQueryName = exports.singleEntityQueryName = void 0;
const graphql_1 = require("graphql");
const json_to_graphql_query_1 = require("json-to-graphql-query");
/**
 * Returns name of query for fetching single entity record
 *
 */
const singleEntityQueryName = (entity) => entity.name.toLowerCase();
exports.singleEntityQueryName = singleEntityQueryName;
/**
 * Returns name of query for fetching multiple entity records
 *
 */
const multiEntityQueryName = (entity) => `${entity.name.toLowerCase()}s`;
exports.multiEntityQueryName = multiEntityQueryName;
/**
 * Generate sample query string based on entity object fields.
 *
 */
const generateQueryForEntity = (entity) => {
    // function to recursively build fields map
    const getObjectFields = (object, queryFields = {}) => {
        const objectFields = object.getFields();
        Object.keys(objectFields).forEach(fieldName => {
            const rawFieldType = objectFields[fieldName].type;
            const fieldType = (0, graphql_1.isWrappingType)(rawFieldType) ? rawFieldType.ofType : rawFieldType;
            if ((0, graphql_1.isLeafType)(fieldType)) {
                queryFields[fieldName] = true;
            }
            else {
                const childObjectFields = {};
                getObjectFields(fieldType, childObjectFields);
                queryFields[fieldName] = childObjectFields;
            }
        });
        return queryFields;
    };
    return (0, json_to_graphql_query_1.jsonToGraphQLQuery)({
        query: {
            [(0, exports.multiEntityQueryName)(entity)]: {
                __args: { first: 10 },
                ...getObjectFields(entity)
            }
        }
    }, { pretty: true });
};
exports.generateQueryForEntity = generateQueryForEntity;
