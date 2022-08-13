import { GraphQLObjectType } from 'graphql';
/**
 * Returns name of query for fetching single entity record
 *
 */
export declare const singleEntityQueryName: (entity: GraphQLObjectType) => string;
/**
 * Returns name of query for fetching multiple entity records
 *
 */
export declare const multiEntityQueryName: (entity: GraphQLObjectType) => string;
/**
 * Generate sample query string based on entity object fields.
 *
 */
export declare const generateQueryForEntity: (entity: GraphQLObjectType) => string;
