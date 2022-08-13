/// <reference types="node" />
import { GraphQLObjectType } from 'graphql';
import { ResolverContext } from './resolvers';
/**
 * Creates an graphql http handler for the query passed a parameters.
 * Returned middleware can be used with express.
 */
export default function get(query: GraphQLObjectType, context: ResolverContext, sampleQuery?: string): (request: import("http").IncomingMessage & {
    url: string;
}, response: import("http").ServerResponse & {
    json?: ((data: unknown) => void) | undefined;
}) => Promise<void>;
/**
 * This objects name and field maps to the values of the _metadata
 * database store
 *
 */
export declare const MetadataGraphQLObject: GraphQLObjectType<any, any>;
/**
 * This objects name and field maps to the values of the _checkpoints
 * database store. And is used to generate entity queries for graphql
 *
 */
export declare const CheckpointsGraphQLObject: GraphQLObjectType<any, any>;
