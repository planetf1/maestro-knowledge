Maestro Knowledge

Usage:
  maestro-k validate YAML_FILE [options]
  maestro-k validate SCHEMA_FILE YAML_FILE [options]

  maestro-k vectordb list [options]
  maestro-k vectordb create YAML_FILE [options]
  maestro-k vectordb delete NAME [options]

  maestro-k collection list --vdb=VDB_NAME [options]
  maestro-k collection create --name=COLLECTION_NAME --vdb=VDB_NAME [options]
  maestro-k collection delete COLLECTION_NAME --vdb=VDB_NAME [options]

  maestro-k embedding list --vdb=VDB_NAME [options]

  maestro-k document list --vdb=VDB_NAME --collection=COLLECTION_NAME [options]
  maestro-k document create --name=DOC_NAME --file=FILE_PATH --vdb=VDB_NAME --collection=COLLECTION_NAME [options]
  maestro-k document delete DOC_NAME --vdb=VDB_NAME --collection=COLLECTION_NAME [options]

  maestro-k query "QUERY_STRING" --vdb=VDB_NAME [options]

  maestro-k (-h | --help)
  maestro-k (-v | --version)

Options:
  --verbose              Show all output.
  --silent               Show no additional output on success, e.g., no OK or Success etc
  --dry-run              Mocks agents and other parts of workflow execution.

  -h --help              Show this screen.
  -v --version           Show version.