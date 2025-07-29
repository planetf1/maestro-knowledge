package main

import (
	"fmt"
	"strings"

	"github.com/spf13/cobra"
)

// CollectionNotFoundError is a custom error type for collection not found errors
type CollectionNotFoundError struct {
	CollectionName string
	VDBName        string
}

func (e *CollectionNotFoundError) Error() string {
	return fmt.Sprintf("Collection '%s' not found in vector database '%s'", e.CollectionName, e.VDBName)
}

var deleteCmd = &cobra.Command{
	Use:   "delete (vector-database | vector-db | vdb) NAME | delete (collection | vdb-col | col) VDB_NAME COLLECTION_NAME",
	Short: "Delete vector database resources",
	Long: `Delete vector database resources by name.
	
Usage:
  maestro-k delete vector-database NAME [options]
  maestro-k delete vector-db NAME [options]
  maestro-k delete vdb NAME [options]
  maestro-k delete collection VDB_NAME COLLECTION_NAME [options]
  maestro-k delete vdb-col VDB_NAME COLLECTION_NAME [options]
  maestro-k delete col VDB_NAME COLLECTION_NAME [options]

Examples:
  maestro-k delete vector-db my-milvus-db
  maestro-k delete vdb my-weaviate-db
  maestro-k delete collection my-milvus-db my-collection
  maestro-k delete col my-weaviate-db my-collection`,
	Args: cobra.RangeArgs(2, 3),
	RunE: func(cmd *cobra.Command, args []string) error {
		// Suppress usage for all errors except usage errors
		cmd.SilenceUsage = true

		resourceType := args[0]

		// Handle vector database deletion (2 args)
		if len(args) == 2 {
			if resourceType == "vector-database" || resourceType == "vector-db" || resourceType == "vdb" {
				name := args[1]
				return deleteVectorDatabase(name)
			}
			// Check if it's a collection resource type that needs 3 args
			if resourceType == "collection" || resourceType == "vdb-col" || resourceType == "col" {
				return fmt.Errorf("collection deletion requires both VDB_NAME and COLLECTION_NAME. Usage: maestro-k delete %s VDB_NAME COLLECTION_NAME", resourceType)
			}
			return fmt.Errorf("unsupported resource type: %s. Use 'vector-database', 'vector-db', or 'vdb'", resourceType)
		}

		// Handle collection deletion (3 args)
		if len(args) == 3 {
			if resourceType == "collection" || resourceType == "vdb-col" || resourceType == "col" {
				vdbName := args[1]
				collectionName := args[2]
				err := deleteCollection(vdbName, collectionName)
				// Suppress usage for collection not found errors
				if _, ok := err.(*CollectionNotFoundError); ok {
					cmd.SilenceUsage = true
				}
				return err
			}
			return fmt.Errorf("unsupported resource type: %s. Use 'collection', 'vdb-col', or 'col'", resourceType)
		}

		return fmt.Errorf("invalid number of arguments")
	},
}

var delCmd = &cobra.Command{
	Use:   "del (vector-database | vector-db | vdb) NAME | del (collection | vdb-col | col) VDB_NAME COLLECTION_NAME",
	Short: "Delete vector database resources (alias for delete)",
	Long: `Delete vector database resources by name (alias for delete command).
	
Usage:
  maestro-k del vector-database NAME [options]
  maestro-k del vector-db NAME [options]
  maestro-k del vdb NAME [options]
  maestro-k del collection VDB_NAME COLLECTION_NAME [options]
  maestro-k del vdb-col VDB_NAME COLLECTION_NAME [options]
  maestro-k del col VDB_NAME COLLECTION_NAME [options]

Examples:
  maestro-k del vector-db my-milvus-db
  maestro-k del vdb my-weaviate-db
  maestro-k del collection my-milvus-db my-collection
  maestro-k del col my-weaviate-db my-collection`,
	Args: cobra.RangeArgs(2, 3),
	RunE: func(cmd *cobra.Command, args []string) error {
		// Suppress usage for all errors except usage errors
		cmd.SilenceUsage = true

		resourceType := args[0]

		// Handle vector database deletion (2 args)
		if len(args) == 2 {
			if resourceType == "vector-database" || resourceType == "vector-db" || resourceType == "vdb" {
				name := args[1]
				return deleteVectorDatabase(name)
			}
			// Check if it's a collection resource type that needs 3 args
			if resourceType == "collection" || resourceType == "vdb-col" || resourceType == "col" {
				return fmt.Errorf("collection deletion requires both VDB_NAME and COLLECTION_NAME. Usage: maestro-k del %s VDB_NAME COLLECTION_NAME", resourceType)
			}
			return fmt.Errorf("unsupported resource type: %s. Use 'vector-database', 'vector-db', or 'vdb'", resourceType)
		}

		// Handle collection deletion (3 args)
		if len(args) == 3 {
			if resourceType == "collection" || resourceType == "vdb-col" || resourceType == "col" {
				vdbName := args[1]
				collectionName := args[2]
				err := deleteCollection(vdbName, collectionName)
				// Suppress usage for collection not found errors
				if _, ok := err.(*CollectionNotFoundError); ok {
					cmd.SilenceUsage = true
				}
				return err
			}
			return fmt.Errorf("unsupported resource type: %s. Use 'collection', 'vdb-col', or 'col'", resourceType)
		}

		return fmt.Errorf("invalid number of arguments")
	},
}

func deleteVectorDatabase(name string) error {
	if verbose {
		fmt.Printf("Deleting vector database: %s\n", name)
	}

	if dryRun {
		if !silent {
			fmt.Printf("[DRY RUN] Would delete vector database '%s'\n", name)
		}
		return nil
	}

	// Validate the name
	if name == "" {
		return fmt.Errorf("vector database name is required")
	}

	// Perform the deletion
	if err := performVectorDatabaseDeletion(name); err != nil {
		return fmt.Errorf("deletion failed: %w", err)
	}

	if !silent {
		fmt.Printf("✅ Vector database '%s' deleted successfully\n", name)
	}

	return nil
}

func deleteCollection(vdbName, collectionName string) error {
	if verbose {
		fmt.Printf("Deleting collection: %s from vector database: %s\n", collectionName, vdbName)
	}

	if dryRun {
		if !silent {
			fmt.Printf("[DRY RUN] Would delete collection '%s' from vector database '%s'\n", collectionName, vdbName)
		}
		return nil
	}

	// Validate the names
	if vdbName == "" {
		return fmt.Errorf("vector database name is required")
	}
	if collectionName == "" {
		return fmt.Errorf("collection name is required")
	}

	// Perform the deletion
	if err := performCollectionDeletion(vdbName, collectionName); err != nil {
		return fmt.Errorf("deletion failed: %w", err)
	}

	if !silent {
		fmt.Printf("✅ Collection '%s' deleted successfully from vector database '%s'\n", collectionName, vdbName)
	}

	return nil
}

func performCollectionDeletion(vdbName, collectionName string) error {
	if verbose {
		fmt.Printf("Deleting collection '%s' from vector database '%s'\n", collectionName, vdbName)
	}

	// Get MCP server URI
	serverURI, err := getMCPServerURI(mcpServerURI)
	if err != nil {
		return fmt.Errorf("failed to get MCP server URI: %w", err)
	}

	if verbose {
		fmt.Printf("Connecting to MCP server at: %s\n", serverURI)
	}

	// Create MCP client
	client, err := NewMCPClient(serverURI)
	if err != nil {
		return fmt.Errorf("failed to create MCP client: %w", err)
	}
	defer client.Close()

	// Check if database exists before deleting collection
	exists, err := client.DatabaseExists(vdbName)
	if err != nil {
		return fmt.Errorf("failed to check if database exists: %w", err)
	}
	if !exists {
		return fmt.Errorf("vector database '%s' does not exist", vdbName)
	}

	// Collection existence check is now handled by the MCP server

	// Call the MCP server to delete the collection with panic recovery
	var deleteErr error
	func() {
		defer func() {
			if r := recover(); r != nil {
				// Convert panic to a user-friendly error
				deleteErr = fmt.Errorf("MCP server could not be reached at %s. Please ensure the server is running and accessible", serverURI)
			}
		}()
		deleteErr = client.DeleteCollection(vdbName, collectionName)
	}()

	if deleteErr != nil {
		// Check if it's a collection not found error and provide cleaner output
		errMsg := deleteErr.Error()
		if strings.Contains(errMsg, "not found in vector database") {
			// Extract the collection name and vdb name from the error message
			// Error format: "Collection 'collection_name' not found in vector database 'vdb_name'"
			return &CollectionNotFoundError{CollectionName: collectionName, VDBName: vdbName}
		}
		// For other errors, wrap with context
		return fmt.Errorf("failed to delete collection: %w", deleteErr)
	}

	if verbose {
		fmt.Println("Collection deletion completed successfully")
	}

	return nil
}

func performVectorDatabaseDeletion(name string) error {
	if verbose {
		fmt.Printf("Deleting vector database '%s'\n", name)
	}

	// Get MCP server URI
	serverURI, err := getMCPServerURI(mcpServerURI)
	if err != nil {
		return fmt.Errorf("failed to get MCP server URI: %w", err)
	}

	if verbose {
		fmt.Printf("Connecting to MCP server at: %s\n", serverURI)
	}

	// Create MCP client
	client, err := NewMCPClient(serverURI)
	if err != nil {
		return fmt.Errorf("failed to create MCP client: %w", err)
	}
	defer client.Close()

	// Check if database exists before deleting
	exists, err := client.DatabaseExists(name)
	if err != nil {
		return fmt.Errorf("failed to check if database exists: %w", err)
	}
	if !exists {
		return fmt.Errorf("vector database '%s' does not exist", name)
	}

	// Call the MCP server to delete the database with panic recovery
	var deleteErr error
	func() {
		defer func() {
			if r := recover(); r != nil {
				// Convert panic to a user-friendly error
				deleteErr = fmt.Errorf("MCP server could not be reached at %s. Please ensure the server is running and accessible", serverURI)
			}
		}()
		deleteErr = client.DeleteVectorDatabase(name)
	}()

	if deleteErr != nil {
		return fmt.Errorf("failed to delete vector database: %w", deleteErr)
	}

	if verbose {
		fmt.Println("Vector database deletion completed successfully")
	}

	return nil
}
