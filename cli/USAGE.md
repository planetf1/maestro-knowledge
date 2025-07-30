Maestro Knowledge

Usage:
  maestro-k validate YAML_FILE [options]
  maestro-k validate SCHEMA_FILE YAML_FILE [options]

  maestro-k create (vector-database | vector-db | vdb) YAML_FILE [options]
  maestro-k create (collection | vdb-col | col) VDB_NAME COLLECTION_NAME [options]
  maestro-k create (document | vdb-doc | doc) VDB_NAME COLLECTION_NAME DOC_NAME --file-name=FILE_NAME [options]
  
  maestro-k write (document | vdb-doc | doc) VDB_NAME COLLECTION_NAME DOC_NAME --file-name=FILE_NAME [options]
  
  maestro-k delete (vector-database | vector-db | vdb) NAME [options]
  maestro-k delete (collection | vdb-col | col) VDB_NAME COLLECTION_NAME [options]
  maestro-k delete (document | vdb-doc | doc) VDB_NAME COLLECTION_NAME DOC_NAME [options]
  maestro-k del (vector-database | vector-db | vdb) NAME [options]
  maestro-k del (collection | vdb-col | col) VDB_NAME COLLECTION_NAME [options]
  maestro-k del (document | vdb-doc | doc) VDB_NAME COLLECTION_NAME DOC_NAME [options]
  
  maestro-k list (vector-databases | vector-dbs | vdbs) [options]
  maestro-k list (embeddings | embeds | vdb-embeds) VDB_NAME [options]
  maestro-k list (collections | cols | vdb-cols) VDB_NAME [options]
  maestro-k list (documents | docs | vdb-docs) VDB_NAME COLLECTION_NAME [options]
  
  maestro-k retrieve (collection | vdb-col | col) VDB_NAME [COLLECTION_NAME] [options]
  maestro-k retrieve (document | vdb-doc | doc) VDB_NAME COLLECTION_NAME DOC_NAME [options]
  maestro-k get (collection | vdb-col | col) VDB_NAME [COLLECTION_NAME] [options]
  maestro-k get (document | vdb-doc | doc) VDB_NAME COLLECTION_NAME DOC_NAME [options]

  maestro-k (-h | --help)
  maestro-k (-v | --version)

Options:
  --verbose              Show all output.
  --silent               Show no additional output on success, e.g., no OK or Success etc
  --dry-run              Mocks agents and other parts of workflow execution.

  -h --help              Show this screen.
  -v --version           Show version.