package main

import (
	"fmt"

	"github.com/spf13/cobra"
)

var listCmd = &cobra.Command{
	Use:   "list (vector-database | vector-db | vdb | embeddings | embed | vdb-embed) [VDB_NAME]",
	Short: "List vector database resources or embeddings",
	Long: `List vector database resources or embeddings.

Usage:
  maestro-k list vector-database [options]
  maestro-k list vector-db [options]
  maestro-k list vdb [options]
  maestro-k list embeddings VDB_NAME [options]
  maestro-k list embed VDB_NAME [options]
  maestro-k list vdb-embed VDB_NAME [options]

Examples:
  maestro-k list vector-db
  maestro-k list vector-database --verbose
  maestro-k list vdb --mcp-server-uri=http://localhost:8000
  maestro-k list embeddings my-database
  maestro-k list embed my-database --verbose`,
	Args: cobra.MinimumNArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		resourceType := args[0]

		// Handle embeddings subcommand
		if resourceType == "embeddings" || resourceType == "embed" || resourceType == "vdb-embed" {
			if len(args) < 2 {
				return fmt.Errorf("VDB_NAME is required for embeddings command")
			}
			vdbName := args[1]
			return listEmbeddings(vdbName)
		}

		// Validate resource type for vector databases
		if resourceType != "vector-database" && resourceType != "vector-db" && resourceType != "vdb" {
			return fmt.Errorf("unsupported resource type: %s. Use 'vector-database', 'vector-db', 'vdb', 'embeddings', 'embed', or 'vdb-embed'", resourceType)
		}

		return listVectorDatabases()
	},
}

func listVectorDatabases() error {
	if verbose {
		fmt.Println("Listing vector databases...")
	}

	if dryRun {
		fmt.Println("[DRY RUN] Would list vector databases")
		return nil
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

	// Call the MCP server to list databases with panic recovery
	var databases []DatabaseInfo
	var listErr error

	func() {
		defer func() {
			if r := recover(); r != nil {
				// Convert panic to a user-friendly error
				listErr = fmt.Errorf("MCP server could not be reached at %s. Please ensure the server is running and accessible", serverURI)
			}
		}()
		databases, listErr = client.ListDatabases()
	}()

	if listErr != nil {
		return fmt.Errorf("failed to list vector databases: %w", listErr)
	}

	// Display results
	if len(databases) == 0 {
		if !silent {
			fmt.Println("No vector databases found")
		}
		return nil
	}

	if !silent {
		fmt.Printf("Found %d vector database(s):\n\n", len(databases))
	}

	for i, db := range databases {
		if !silent {
			fmt.Printf("%d. %s (%s)\n", i+1, db.Name, db.Type)
			fmt.Printf("   Collection: %s\n", db.Collection)
			fmt.Printf("   Documents: %d\n", db.DocumentCount)
			fmt.Println()
		}
	}

	if verbose {
		fmt.Println("Vector database listing completed successfully")
	}

	return nil
}

func listEmbeddings(vdbName string) error {
	if verbose {
		fmt.Printf("Listing embeddings for vector database '%s'...\n", vdbName)
	}

	if dryRun {
		fmt.Printf("[DRY RUN] Would list embeddings for vector database '%s'\n", vdbName)
		return nil
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

	// Check if the database exists first
	exists, err := client.DatabaseExists(vdbName)
	if err != nil {
		return fmt.Errorf("failed to check if database exists: %w", err)
	}

	if !exists {
		return fmt.Errorf("vector database '%s' does not exist. Please create it first", vdbName)
	}

	// Call the MCP server to get embeddings with panic recovery
	var embeddingsResult string
	var embeddingsErr error

	func() {
		defer func() {
			if r := recover(); r != nil {
				// Convert panic to a user-friendly error
				embeddingsErr = fmt.Errorf("MCP server could not be reached at %s. Please ensure the server is running and accessible", serverURI)
			}
		}()
		embeddingsResult, embeddingsErr = client.GetSupportedEmbeddings(vdbName)
	}()

	if embeddingsErr != nil {
		return fmt.Errorf("failed to get embeddings for vector database '%s': %w", vdbName, embeddingsErr)
	}

	// Display results
	if !silent {
		fmt.Println(embeddingsResult)
	}

	if verbose {
		fmt.Printf("Embeddings listing completed successfully for vector database '%s'\n", vdbName)
	}

	return nil
}
