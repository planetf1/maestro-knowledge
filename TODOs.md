# ✅ `list` command

* ✅ add sub-command to return `vector-databases` configured. Usage like:
    ```yaml
    $ maestro-k list (vector-database | vector-db | vdbs) [options]
    ```

* ✅ add sub-command to return `embeddings` that a vdb supports. Usage like:
    ```yaml
    $ maestro-k list (embeddings | embed | vdb-embed) VDB_NAME [options]
    ```

* ✅ add sub-command to return `documents` in a collection of a vdb. CLI usage examples:
    ```yaml
    $ maestro-k list (documents | docs | vdb-docs) VDB_NAME COLLECTION_NAME [options]
    ```

* ✅ add sub-command to return `collections` in a vdb. Usage like:
    ```yaml
    $ maestro-k list (collections | cols | vdb-cols) VDB_NAME [options]
    ```

# `create` command

* add sub-command to `create` a `collection` in a vdb. Usage like:
    ```yaml
    $ maestro-k create (collection | vdb-col | col) VBD_NAME [options]
    ```

* add sub-command to (`create` | `write`) a `document` in a collection of a vdb with a specified embedding or the default if none specified. Usage like:
    ```yaml
    $ maestro-k (create | write) (document | vdb-doc | doc) VBD_NAME COLLECTION_NAME (EMBEDDING_NAME) [options]
    ```

# `delete` command

* add sub-command to (`delete` | `del`) a `collection` in a vdb. Usage like:
    ```yaml
    $ maestro-k (delete | del) (collection | vdb-col | col) VBD_NAME [options]
    ```

* add sub-command to (`delete` | `del`) a `document` in a collection of a vdb. Usage like:
    ```yaml
    $ maestro-k (delete | del) (document | vdb-doc | doc) VBD_NAME COLLECTION_NAME [options]
    ```


# `retrieve` or `get` command

* add sub-command to (`retrieve` | `get`) a `collection` in a vdb. Usage like:
    ```yaml
    $ maestro-k (retrieve | get) (collection | vdb-col | col) VBD_NAME [options]
    ```

* add sub-command to (`retrieve` | `get`) a `document` in a collection of a vdb. Usage like:
    ```yaml
    $ maestro-k (retrieve | get) (document | vdb-doc | doc) VBD_NAME COLLECTION_NAME [options]
    ```

# other

* support `collection_names` as a list of string in agent defintion and MCP server:
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

* add a way to send a query to the vdb default query agent

* add a way to retrieve a maestro agent configuration for the query agent of a vdb

* add a way to retrieve and query the maestro agent config for the query agent of a vbd