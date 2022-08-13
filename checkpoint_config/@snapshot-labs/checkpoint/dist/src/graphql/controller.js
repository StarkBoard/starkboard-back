"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.GqlEntityController = void 0;
const graphql_1 = require("graphql");
const graphql_2 = require("../utils/graphql");
const resolvers_1 = require("./resolvers");
const GraphQLOrderDirection = new graphql_1.GraphQLEnumType({
    name: 'OrderDirection',
    values: {
        asc: { value: 'ASC' },
        desc: { value: 'DESC' }
    }
});
/**
 * Controller for performing actions based on the graphql schema provided to its
 * constructor. It exposes public functions to generate graphql or database
 * items based on the entities identified in the schema.
 *
 * Note: Entities refer to Object types with an `id` field defined within the
 * graphql schema.
 */
class GqlEntityController {
    schema;
    _schemaObjects;
    constructor(typeDefs) {
        this.schema = (0, graphql_1.buildSchema)(typeDefs);
    }
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
    generateQueryFields(schemaObjects, resolvers = {
        singleEntityResolver: resolvers_1.querySingle,
        multipleEntityResolver: resolvers_1.queryMulti
    }) {
        schemaObjects = schemaObjects || this.schemaObjects;
        const queryFields = {};
        schemaObjects.forEach(type => {
            queryFields[(0, graphql_2.singleEntityQueryName)(type)] = this.getSingleEntityQueryConfig(type, resolvers.singleEntityResolver);
            queryFields[(0, graphql_2.multiEntityQueryName)(type)] = this.getMultipleEntityQueryConfig(type, resolvers.multipleEntityResolver);
        });
        return queryFields;
    }
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
    async createEntityStores(mysql) {
        if (this.schemaObjects.length === 0) {
            return;
        }
        let sql = '';
        this.schemaObjects.forEach(type => {
            sql += `\n\nDROP TABLE IF EXISTS ${type.name.toLowerCase()}s;`;
            sql += `\nCREATE TABLE ${type.name.toLowerCase()}s (`;
            let sqlIndexes = ``;
            this.getTypeFields(type).forEach(field => {
                const sqlType = this.getSqlType(field.type);
                sql += `\n  ${field.name} ${sqlType}`;
                if (field.type instanceof graphql_1.GraphQLNonNull) {
                    sql += ' NOT NULL,';
                }
                else {
                    sql += ',';
                }
                if (sqlType !== 'TEXT') {
                    sqlIndexes += `,\n  INDEX ${field.name} (${field.name})`;
                }
            });
            sql += `\n  PRIMARY KEY (id) ${sqlIndexes}\n);\n`;
        });
        // TODO(perfectmak): wrap this in a transaction
        return mysql.queryAsync(sql.trimEnd());
    }
    /**
     * Generates a query based on the first entity discovered
     * in a schema. If no entities are found in the schema
     * it returns undefined.
     *
     */
    generateSampleQuery() {
        if (this.schemaObjects.length === 0) {
            return undefined;
        }
        const firstEntityQuery = (0, graphql_2.generateQueryForEntity)(this.schemaObjects[0]);
        const queryComment = `
# Welcome to Checkpoint. Try running the below example query from 
# your defined entity.
    `;
        return `${queryComment}\n${firstEntityQuery}`;
    }
    /**
     * Returns a list of objects defined within the graphql typedefs.
     * The types returns are introspection objects, that can be used
     * for inspecting the fields and types.
     *
     * Note: that the returned objects does not include the Query object type if defined.
     *
     */
    get schemaObjects() {
        if (this._schemaObjects) {
            return this._schemaObjects;
        }
        this._schemaObjects = Object.values(this.schema.getTypeMap()).filter(type => {
            return (type instanceof graphql_1.GraphQLObjectType && type.name != 'Query' && !type.name.startsWith('__'));
        });
        return this._schemaObjects;
    }
    getTypeFields(type) {
        return Object.values(type.getFields());
    }
    getSingleEntityQueryConfig(type, resolver) {
        return {
            type,
            args: {
                id: { type: new graphql_1.GraphQLNonNull(this.getEntityIdType(type)) }
            },
            resolve: resolver
        };
    }
    getMultipleEntityQueryConfig(type, resolver) {
        const whereInputConfig = {
            name: `Where${type.name}`,
            fields: {}
        };
        const orderByValues = {};
        this.getTypeFields(type).forEach(field => {
            // all field types in a where input variable must be optional
            // so we try to extract the non null type here.
            const nonNullFieldType = this.getNonNullType(field.type);
            // avoid setting up where filters for non scalar types
            if (!(0, graphql_1.isLeafType)(nonNullFieldType)) {
                return;
            }
            if (nonNullFieldType === graphql_1.GraphQLInt) {
                whereInputConfig.fields[`${field.name}_gt`] = { type: graphql_1.GraphQLInt };
                whereInputConfig.fields[`${field.name}_gte`] = { type: graphql_1.GraphQLInt };
                whereInputConfig.fields[`${field.name}_lt`] = { type: graphql_1.GraphQLInt };
                whereInputConfig.fields[`${field.name}_lte`] = { type: graphql_1.GraphQLInt };
            }
            if (nonNullFieldType.name !== 'Text') {
                whereInputConfig.fields[`${field.name}`] = { type: nonNullFieldType };
                whereInputConfig.fields[`${field.name}_in`] = {
                    type: new graphql_1.GraphQLList(nonNullFieldType)
                };
            }
            // add fields to orderBy enum
            orderByValues[field.name] = { value: field.name };
        });
        const OrderByEnum = new graphql_1.GraphQLEnumType({
            name: `OrderBy${type.name}Fields`,
            values: orderByValues
        });
        return {
            type: new graphql_1.GraphQLList(type),
            args: {
                first: {
                    type: graphql_1.GraphQLInt
                },
                skip: {
                    type: graphql_1.GraphQLInt
                },
                orderBy: {
                    type: OrderByEnum
                },
                orderDirection: {
                    type: GraphQLOrderDirection
                },
                where: { type: new graphql_1.GraphQLInputObjectType(whereInputConfig) }
            },
            resolve: resolver
        };
    }
    getEntityIdType(type) {
        const idField = type.getFields().id;
        if (!idField) {
            throw new Error(`'id' field is missing in type '${type.name}'. All types are required to have an id field.`);
        }
        if (!(idField.type instanceof graphql_1.GraphQLNonNull)) {
            throw new Error(`'id' field for type ${type.name} must be non nullable.`);
        }
        const nonNullType = idField.type.ofType;
        // verify only scalar types are used
        if (!(nonNullType instanceof graphql_1.GraphQLScalarType)) {
            throw new Error(`'id' field for type ${type.name} is not a scalar type.`);
        }
        return nonNullType;
    }
    getNonNullType(type) {
        if (type instanceof graphql_1.GraphQLNonNull) {
            return type.ofType;
        }
        return type;
    }
    /**
     * Return a mysql column type for the graphql type.
     *
     * It throws if the type is not a recognized scalar type.
     */
    getSqlType(type) {
        if (type instanceof graphql_1.GraphQLNonNull) {
            type = type.ofType;
        }
        switch (type) {
            case graphql_1.GraphQLInt:
                return 'INT(128)';
            case graphql_1.GraphQLFloat:
                return 'FLOAT(23)';
            case graphql_1.GraphQLString:
            case graphql_1.GraphQLID:
                return 'VARCHAR(128)';
        }
        // check for TEXT scalar type
        if (type instanceof graphql_1.GraphQLScalarType && type.name === 'Text') {
            return 'TEXT';
        }
        // TODO(perfectmak): Add support for List types
        throw new Error(`sql type for ${type} not support`);
    }
}
exports.GqlEntityController = GqlEntityController;
