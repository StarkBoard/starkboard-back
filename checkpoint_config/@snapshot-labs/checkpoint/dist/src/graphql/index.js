"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CheckpointsGraphQLObject = exports.MetadataGraphQLObject = void 0;
const express_graphql_1 = require("express-graphql");
const graphql_1 = require("graphql");
/**
 * Creates an graphql http handler for the query passed a parameters.
 * Returned middleware can be used with express.
 */
function get(query, context, sampleQuery) {
    const schema = new graphql_1.GraphQLSchema({ query });
    return (0, express_graphql_1.graphqlHTTP)({
        schema,
        context,
        graphiql: {
            defaultQuery: sampleQuery
        }
    });
}
exports.default = get;
/**
 * This objects name and field maps to the values of the _metadata
 * database store
 *
 */
exports.MetadataGraphQLObject = new graphql_1.GraphQLObjectType({
    name: '_Metadata',
    description: 'Core metadata values used internally by Checkpoint',
    fields: {
        id: { type: new graphql_1.GraphQLNonNull(graphql_1.GraphQLID), description: 'example: last_indexed_block' },
        value: { type: graphql_1.GraphQLString }
    }
});
/**
 * This objects name and field maps to the values of the _checkpoints
 * database store. And is used to generate entity queries for graphql
 *
 */
exports.CheckpointsGraphQLObject = new graphql_1.GraphQLObjectType({
    name: '_Checkpoint',
    description: 'Contract and Block where its event is found.',
    fields: {
        id: {
            type: new graphql_1.GraphQLNonNull(graphql_1.GraphQLID),
            description: 'id computed as last 5 bytes of sha256(contract+block)'
        },
        block_number: {
            type: new graphql_1.GraphQLNonNull(graphql_1.GraphQLInt)
        },
        contract_address: {
            type: new graphql_1.GraphQLNonNull(graphql_1.GraphQLString)
        }
    }
});
