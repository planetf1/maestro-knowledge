# Vector Database Configuration Schema

This directory contains JSON schemas for validating Maestro vector database configurations with support for environment variable substitution.

## Files

- `vector-database-schema.json` - JSON schema for vector database configurations

## Schema Overview

The schema validates vector database configurations with the following structure:

```yaml
apiVersion: maestro/v1alpha1
kind: VectorDatabase
metadata:
  name: <unique-name>
  labels:
    app: <app-label>
spec:
  type: milvus|weaviate
  uri: <connection-uri>
  collection_name: <collection-name>
  embedding: <embedding-model>
  mode: local|remote
```

## Validation Rules

### Required Fields
- `apiVersion`: Must be exactly "maestro/v1alpha1"
- `kind`: Must be "VectorDatabase"
- `metadata.name`: Unique name for the configuration
- `spec.type`: Must be either "milvus" or "weaviate"
- `spec.uri`: Connection URI (host:port for local, full URL for remote)
- `spec.collection_name`: Name of the collection
- `spec.embedding`: Embedding model identifier
- `spec.mode`: Must be either "local" or "remote"

### Optional Fields
- `metadata.labels`: Key-value pairs for labeling
- `metadata.labels.app`: Application label (common pattern)

## Environment Variable Substitution

The CLI tool supports environment variable substitution in YAML files using the `{{ENV_VAR_NAME}}` syntax. This allows you to use environment variables directly in your configuration files:

```yaml
apiVersion: maestro/v1alpha1
kind: VectorDatabase
metadata:
  name: my-weaviate-db
spec:
  type: weaviate
  uri: {{WEAVIATE_URL}}
  collection_name: my_collection
  embedding: text-embedding-3-small
  mode: remote
```

### Features

- **Automatic substitution**: All `{{ENV_VAR_NAME}}` placeholders are replaced before YAML parsing
- **Error handling**: Clear error messages if required environment variables are missing
- **Verbose logging**: Shows which environment variables are being substituted (when using `--verbose`)
- **Validation**: Ensures all required environment variables are set before processing

## Usage

### Using the Schema with Tests

The schema is validated against the example YAML files in the test suite:

```bash
# Run the YAML validation tests
pytest tests/test_vector_database_yamls.py -v
```

### Using the Schema with CLI

The CLI tool automatically validates YAML files when creating vector databases:

```bash
# Validate YAML configuration
./maestro-k validate config.yaml

# Create vector database with validation
./maestro-k vectordb create config.yaml
```

### Using the Schema Directly

You can use any JSON schema validator with the `vector-database-schema.json` file. The schema follows JSON Schema Draft-07 specification.

## Example Valid Configurations

### Local Milvus
```yaml
apiVersion: maestro/v1alpha1
kind: VectorDatabase
metadata:
  name: local_milvus
  labels:
    app: testdb
spec:
  type: milvus
  uri: localhost:19530
  collection_name: test_collection
  embedding: text-embedding-3-small
  mode: local
```

### Remote Weaviate
```yaml
apiVersion: maestro/v1alpha1
kind: VectorDatabase
metadata:
  name: remote_weaviate
  labels:
    app: testdb
spec:
  type: weaviate
  uri: https://your-weaviate-cluster.weaviate.network
  collection_name: test_collection
  embedding: text-embedding-3-small
  mode: remote
```

### With Environment Variables
```yaml
apiVersion: maestro/v1alpha1
kind: VectorDatabase
metadata:
  name: dynamic_weaviate
  labels:
    app: production
spec:
  type: weaviate
  uri: {{WEAVIATE_URL}}
  collection_name: {{COLLECTION_NAME}}
  embedding: {{EMBEDDING_MODEL}}
  mode: {{DEPLOYMENT_MODE}}
```

## Dependencies

To use the validation script, install the required dependencies:

```bash
pip install pyyaml jsonschema
```

Or using uv:

```bash
uv add pyyaml jsonschema
``` 