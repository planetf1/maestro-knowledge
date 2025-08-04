# ✅ `list` command

* ✅ add sub-command to return `vector-databases` configured. Usage like:
    ```bash
    $ maestro-k list (vector-database | vector-db | vdbs) [options]
    ```

* ✅ add sub-command to return `embeddings` that a vdb supports. Usage like:
    ```bash
    $ maestro-k list (embeddings | embed | vdb-embed) VDB_NAME [options]
    ```

* ✅ add sub-command to return `documents` in a collection of a vdb. CLI usage examples:
    ```bash
    $ maestro-k list (documents | docs | vdb-docs) VDB_NAME COLLECTION_NAME [options]
    ```

* ✅ add sub-command to return `collections` in a vdb. Usage like:
    ```bash
    $ maestro-k list (collections | cols | vdb-cols) VDB_NAME [options]
    ```

# ✅ `create` command

* ✅ add sub-command to `create` a `collection` in a vdb. Usage like:
    ```bash
    $ maestro-k create (collection | vdb-col | col) VBD_NAME [options]
    ```

* ✅ add sub-command to (`create` | `write`) a `document` in a collection of a vdb with a specified embedding or the default if none specified. Some notes for errors:

  - If specified the `embedding` or `embed` must exist when listing embedding for the vdb otherwise the comamnd should fail. If not specified the embedding will be the default embedding
  - VBD_NAME must refer to an existing vdb -- in other words in the list of vdbs
  - COL_NAME must refer to an existing collection -- in other words in the list of collections for this vdb
  - DOC_NAME must be unique - such that no other documents in the collection in this vdb already has that name

Usage like:
    ```bash
    $ maestro-k create (document | vdb-doc | doc) VBD_NAME COL_NAME DOC_NAME --doc-file-name=DOC_FILE_NAME [options] 
    $ maestro-k create (document | vdb-doc | doc) VBD_NAME COL_NAME DOC_NAME --file-name=DOC_FILE_NAME --embed=EMBEDDING_NAME [options]
    
    $ maestro-k write (document | vdb-doc | doc) VBD_NAME COL_NAME DOC_NAME --doc-file-name=DOC_FILE_NAME [options]
    $ maestro-k write (document | vdb-doc | doc) VBD_NAME COL_NAME DOC_NAME --file-name=DOC_FILE_NAME --embed=EMBEDDING_NAME [options]
    ```

# ✅ `delete` command

* ✅ add sub-command to (`delete` | `del`) a `collection` in a vdb. Some notes for errors:
  - VBD_NAME must refer to an existing vdb -- in other words in the list of vdbs
  - COL_NAME must refer to an existing collection -- in other words in the list of collections for this vdb

Usage like:
    ```bash
    $ maestro-k delete (collection | vdb-col | col) VDB_NAME COL_NAME [options]
    $ maestro-k del (collection | vdb-col | col) VDB_NAME COL_NAME [options]
    ```

* ✅ add sub-command to (`delete` | `del`) a `document` in a collection of a vdb. Some notes for errors:
  - VBD_NAME must refer to an existing vdb -- in other words in the list of vdbs
  - COL_NAME must refer to an existing collection -- in other words in the list of collections for this vdb
  - DOC_NAME must refer to an existing document in that collection

Usage like:
    ```bash
    $ maestro-k delete (document | vdb-doc | doc) VBD_NAME COL_NAME DOC_NAME [options]
    $ maestro-k del (document | vdb-doc | doc) VBD_NAME COL_NAME DOC_NAME [options]
    ```

# ✅ `retrieve` or `get` command

* ✅ add sub-command to (`retrieve` | `get`) a `collection` in a vdb. Some notes for errors:
  - VBD_NAME must refer to an existing vdb -- in other words in the list of vdbs
Usage like:
    ```bash
    $ maestro-k retrieve (collection | vdb-col | col) VBD_NAME [options]
    $ maestro-k get (collection | vdb-col | col) VBD_NAME [options]
    ```

* ✅ add sub-command to (`retrieve` | `get`) a `document` in a collection of a vdb. Some notes for errors:
  - VBD_NAME must refer to an existing vdb -- in other words in the list of vdbs
  - COL_NAME must refer to an existing collection -- in other words in the list of collections for this vdb
  - DOC_NAME must refer to an existing document in that collection
Usage like:
    ```bash
    $ maestro-k retrieve (document | vdb-doc | doc) VDB_NAME COL_NAME DOC_NAME [options]
    $ maestro-k get (document | vdb-doc | doc) VDB_NAME COL_NAME DOC_NAME [options]
    ```
# ✅ `query` command

* add a way to send a query to the vdb default query agent. This should:

  - include a `query(string) -> string` function to the MCP server 
  - corresponding `query VDB COL_NAME QUERY` command to the CLI
  - changes to the VDB abstraction to support `query` and creating default query agent that can be used to perform the query. 
    An example of this abstraction and implementation for Weeviate and Milvus is in the RAGme-ai project at: https://github.com/maximilien/ragme-ai

# other

* ✅ change "SPDX-License-Identifier: MIT" in source and tests files in this repo to "SPDX-License-Identifier: Apache 2.0" since that's the LICENSE we are using and "Copyright (c) 2025 dr.max" to "Copyright (c) 2025 IBM"

* ✅ clean up tools scripts into one directory

* ✅ add ./tools/e2e.sh script

* ✅ move CLI examples before Python examples in README

* ✅ add recommended development workflow for contributions

**OPEN**

* clean up code /tests (remove duplicate and refactor) and ensure consistency in CLI commands and tests

* review CLI commands for UI / UX in terms of ease of use

* add a `create query` command as a way to retrieve a maestro agent configuration (YAML) for the query agent of a vdb

* a few bugs remain
- test-integration.sh still pollutes tests db and should leave it empty

* add a way to retrieve and query the maestro agent config for the query agent of a vbd

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