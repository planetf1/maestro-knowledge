0. support `collection_names` as a list of string in agent defintion and MCP server:
    ```yaml
    apiVersion: maestro/v1alpha1
    kind: VectorDatabase
    metadata:
    name: test_local_milvus
    labels:
        app: testdb
    spec:
    type: milvus
    uri: localhost:19530
    collection_names: 
        - test_collection0
        - test_collection1
        - test_collection2
    embedding: text-embedding-3-small
    mode: local
    ```
    This implies changes to the schema, examlpes, and might also imply changes to MCP server functions and CLI to take the collection_name as a required parameter since there could be many collections in the VectorDatabase. One idea is to have a `get_collection_names_tool` for a VectorDatabase. 

1. add CLI to create, delete, and list document(s) in a vdb. CLI usage examples:
    $ maestro-k create (document | doc | vdb-doc) (YAML_FILE | JSON_FILE) VDB_NAME COLLECTION_NAME [options]
    $ maestro-k delete (document | doc | vdb-doc) DOC_ID VDB_NAME COLLECTION_NAME [options]
    $ maestro-k list (documents | docs | vdb-docs) VDB_NAME COLLECTION_NAME [options]

2. add a way to send a query to the vdb default query agent

3. add a way to retrieve a maestro agent configuration for the query agent of a vdb

4. add a way to retrieve and query the maestro agent config for the query agent of a vbd