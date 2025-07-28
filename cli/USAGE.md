Maestro Knowledge

Usage:
  maestro-k validate YAML_FILE [options]
  maestro-k validate SCHEMA_FILE YAML_FILE [options]

  maestro-k create (vector-database | vector-db) YAML_FILE [options]
  maestro-k delete (vector-database | vector-db) NAME [options]
  maestro-k list (vector-databases | vector-dbs | vdbs) [options]
  maestro-k list (embeddings | embeds | vdb-embeds) VDB_NAME [options]
  maestro-k list (collections | cols | vdb-cols) VDB_NAME [options]
  maestro-k list (documents | docs | vdb-docs) VDB_NAME COLLECTION_NAME [options]

  maestro-k (-h | --help)
  maestro-k (-v | --version)

Options:
  --verbose              Show all output.
  --silent               Show no additional output on success, e.g., no OK or Success etc
  --dry-run              Mocks agents and other parts of workflow execution.

  -h --help              Show this screen.
  -v --version           Show version.