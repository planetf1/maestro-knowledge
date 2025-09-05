# TODOs

## OPENED

### CLI
* CLI has been moved to separate repository: AI4quantum/maestro-cli
* add a `create query` command as a way to retrieve a maestro agent configuration (YAML) for the query agent of a vdb

### chore
* clean up code /tests (remove duplicate and refactor)

### feature
* add a way to retrieve and query the maestro agent config for the query agent of a vbd
* support `collection_names` as a list of string in agent definition and MCP server:
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
    This implies changes to the schema, examples, and might also imply changes to MCP server functions and CLI to take the collection_name as a required parameter since there could be many collections in the VectorDatabase. One idea is to have a `get_collection_names_tool` for a VectorDatabase.

### MCP
* add a way to send a query to the vdb default query agent. This should:
  - include a `query(string) -> string` function to the MCP server 
  - corresponding `query VDB COL_NAME QUERY` command to the CLI
  - changes to the VDB abstraction to support `query` and creating default query agent that can be used to perform the query. 
    An example of this abstraction and implementation for Weaviate and Milvus is in the RAGme-ai project at: https://github.com/maximilien/ragme-ai

### other
* a few bugs remain
  - ✅ test-integration.sh still pollutes tests db and should leave it empty
  - ✅ fix Go version mismatch in CI
  - ✅ fix golangci-lint compatibility issues

## COMPLETED

### CLI
* ✅ add sub-command to return `vector-databases` configured. Usage like:
    ```bash
    $ maestro vectordb list [options]
    ```

* ✅ add sub-command to return `embeddings` that a vdb supports. Usage like:
    ```bash
    $ maestro embedding list --vdb=VDB_NAME [options]
    ```

* ✅ add sub-command to return `documents` in a collection of a vdb. CLI usage examples:
    ```bash
    $ maestro document list --vdb=VDB_NAME --collection=COLLECTION_NAME [options]
    ```

* ✅ add sub-command to return `collections` in a vdb. Usage like:
    ```bash
    $ maestro collection list --vdb=VDB_NAME [options]
    ```

* ✅ add sub-command to `create` a `collection` in a vdb. Usage like:
    ```bash
    $ maestro collection create --name=COLLECTION_NAME --vdb=VDB_NAME [options]
    ```

* ✅ add sub-command to `create` a `document` in a collection of a vdb with a specified embedding or the default if none specified. Some notes for errors:
  - If specified the `embedding` must exist when listing embedding for the vdb otherwise the command should fail. If not specified the embedding will be the default embedding
  - VDB_NAME must refer to an existing vdb -- in other words in the list of vdbs
  - COLLECTION_NAME must refer to an existing collection -- in other words in the list of collections for this vdb
  - DOC_NAME must be unique - such that no other documents in the collection in this vdb already has that name

Usage like:
    ```bash
    $ maestro document create --name=DOC_NAME --file=DOC_FILE_NAME --vdb=VDB_NAME --collection=COLLECTION_NAME [options] 
    $ maestro document create --name=DOC_NAME --file=DOC_FILE_NAME --vdb=VDB_NAME --collection=COLLECTION_NAME --embedding=EMBEDDING_NAME [options]
    ```

* ✅ add sub-command to `delete` a `collection` in a vdb. Some notes for errors:
  - VDB_NAME must refer to an existing vdb -- in other words in the list of vdbs
  - COLLECTION_NAME must refer to an existing collection -- in other words in the list of collections for this vdb

Usage like:
    ```bash
    $ maestro collection delete COLLECTION_NAME --vdb=VDB_NAME [options]
    ```

* ✅ add sub-command to `delete` a `document` in a collection of a vdb. Some notes for errors:
  - VDB_NAME must refer to an existing vdb -- in other words in the list of vdbs
  - COLLECTION_NAME must refer to an existing collection -- in other words in the list of collections for this vdb
  - DOC_NAME must refer to an existing document in that collection

Usage like:
    ```bash
    $ maestro document delete DOC_NAME --vdb=VDB_NAME --collection=COLLECTION_NAME [options]
    ```

* ✅ add sub-command to `list` a `collection` in a vdb. Some notes for errors:
  - VDB_NAME must refer to an existing vdb -- in other words in the list of vdbs
Usage like:
    ```bash
    $ maestro collection list --vdb=VDB_NAME [options]
    ```

* ✅ add sub-command to `list` `documents` in a collection of a vdb. Some notes for errors:
  - VDB_NAME must refer to an existing vdb -- in other words in the list of vdbs
  - COLLECTION_NAME must refer to an existing collection -- in other words in the list of collections for this vdb
Usage like:
    ```bash
    $ maestro document list --vdb=VDB_NAME --collection=COLLECTION_NAME [options]
    ```

### chore
* ✅ change "SPDX-License-Identifier: MIT" in source and tests files in this repo to "SPDX-License-Identifier: Apache 2.0" since that's the LICENSE we are using and "Copyright (c) 2025 dr.max" to "Copyright (c) 2025 IBM"
* ✅ clean up tools scripts into one directory
* ✅ add ./tools/e2e.sh script
* ✅ move CLI examples before Python examples in README
* ✅ add recommended development workflow for contributions
* ✅ update `stop.sh status` script to be more like RAGme equivalent showing a nice summary status on services
* ✅ add `tools/tail-logs.sh` script adapted from RAGme-ai for log monitoring
* ✅ review CLI commands for UI / UX in terms of ease of use
* ✅ implement CLI UX improvements based on review findings:
  - ✅ simplify command structure by removing redundant commands (delete/del, retrieve/get, query/query vdb)
  - ✅ standardize command patterns to use consistent argument structures
  - ✅ improve error messages to be concise by default and detailed only in verbose mode
  - ✅ add confirmation prompts for destructive operations
  - ✅ improve Go code quality with comprehensive linting:
  - ✅ Added staticcheck for unused code detection
  - ✅ Added golangci-lint for advanced Go linting
  - ✅ Integrated linting into CI/CD pipelines
  - ✅ Updated documentation to reflect linting capabilities
  - ✅ Added quality gates to prevent merging code with linting issues
  - ✅ Add suggestions: "Did you mean..." for typos
  - ✅ Add examples: Show correct usage for common mistakes
  - ✅ Contextual help: Show relevant commands after operations
  - ✅ Workflow guidance: Suggest next steps after operations
  - ✅ Resource selection: Interactive menus for choosing VDBs/collections
  - ✅ Auto-completion: For resource names and file paths 
  - ✅ Status commands: Quick overview of current state
  - ✅ Progress indicators: For long-running operations
* ✅ fix Go version mismatch in CI (golangci-lint compatibility with Go 1.24.1)
* ✅ remove documentation duplications between README files

### feature
* (No completed features yet)

### MCP
* (No completed MCP items yet)

### other
* (No completed other items yet) 