package main

import (
	"fmt"

	"github.com/spf13/cobra"
)

var deleteCmd = &cobra.Command{
	Use:   "delete (vector-database | vector-db) NAME",
	Short: "Delete vector database resources",
	Long: `Delete vector database resources by name.
	
Usage:
  maestro-k delete vector-database NAME [options]
  maestro-k delete vector-db NAME [options]

Examples:
  maestro-k delete vector-db my-milvus-db
  maestro-k delete vector-database my-weaviate-db`,
	Args: cobra.ExactArgs(2),
	RunE: func(cmd *cobra.Command, args []string) error {
		resourceType := args[0]
		name := args[1]

		// Validate resource type
		if resourceType != "vector-database" && resourceType != "vector-db" {
			return fmt.Errorf("unsupported resource type: %s. Use 'vector-database' or 'vector-db'", resourceType)
		}

		return deleteVectorDatabase(name)
	},
}

func deleteVectorDatabase(name string) error {
	if verbose {
		fmt.Printf("Deleting vector database: %s\n", name)
	}

	if dryRun {
		fmt.Printf("[DRY RUN] Would delete vector database '%s'\n", name)
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
