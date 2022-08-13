import { GraphQLFieldConfigMap, GraphQLFieldResolver, GraphQLObjectType, Source } from 'graphql';
import { AsyncMySqlPool } from '../mysql';
import { ResolverContext } from './resolvers';
/**
 * Type for single and multiple query resolvers
 */
interface EntityQueryResolvers<Context = ResolverContext> {
    singleEntityResolver: GraphQLFieldResolver<unknown, Context>;
    multipleEntityResolver: GraphQLFieldResolver<unknown, Context>;
}
/**
 * Controller for performing actions based on the graphql schema provided to its
 * constructor. It exposes public functions to generate graphql or database
 * items based on the entities identified in the schema.
 *
 * Note: Entities refer to Object types with an `id` field defined within the
 * graphql schema.
 */
export declare class GqlEntityController {
    private readonly schema;
    private _schemaObjects?;
    constructor(typeDefs: string | Source);
    /**
     * Creates a grqphql Query object generated from the objects defined within
     * the schema.
     * For each of the objects, two queries are created, one for querying the object
     * by it's id and the second for querying multiple objects based on a couple
     * of parameters.
     *
     * For example, given the input schema:
     * ```
     * type Vote {
     *  id: Int!
     *  name: String
     * }
     * ```
     *
     * The generated queries will be like:
     * ```
     * type Query {
     *  votes(
     *     first: Int
     *     skip: Int
     *     orderBy: String
     *     orderDirection: String
     *     where: WhereVote
     *   ): [Vote]
     *   vote(id: Int!): Vote
     * }
     *
     *  input WhereVote {
     *    id: Int
     *    id_in: [Int]
     *    name: String
     *    name_in: [String]
     *  }
     *
     * ```
     *
     */
    generateQueryFields(schemaObjects?: GraphQLObjectType[], resolvers?: EntityQueryResolvers): GraphQLFieldConfigMap<any, any>;
    /**
     * Creates store for each of the objects in the schema.
     * For now, it only creates mysql tables for each of the objects.
     * It also creates a checkpoint table to track checkpoints visited.
     *
     * For example, given an schema like:
     * ```graphql
     * type Vote {
     *  id: Int!
     *  name: String
     * }
     * ```
     *
     * will execute the following SQL:
     * ```sql
     * DROP TABLE IF EXISTS votes;
     * CREATE TABLE votes (
     *   id VARCHAR(128) NOT NULL,
     *   name VARCHAR(128),
     *   PRIMARY KEY (id) ,
     *   INDEX id (id),
     *   INDEX name (name)
     * );
     * ```
     *
     */
    createEntityStores(mysql: AsyncMySqlPool): Promise<void>;
    /**
     * Generates a query based on the first entity discovered
     * in a schema. If no entities are found in the schema
     * it returns undefined.
     *
     */
    generateSampleQuery(): string | undefined;
    /**
     * Returns a list of objects defined within the graphql typedefs.
     * The types returns are introspection objects, that can be used
     * for inspecting the fields and types.
     *
     * Note: that the returned objects does not include the Query object type if defined.
     *
     */
    private get schemaObjects();
    private getTypeFields;
    private getSingleEntityQueryConfig;
    private getMultipleEntityQueryConfig;
    private getEntityIdType;
    private getNonNullType;
    /**
     * Return a mysql column type for the graphql type.
     *
     * It throws if the type is not a recognized scalar type.
     */
    private getSqlType;
}
export {};
