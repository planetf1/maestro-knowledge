package main

import (
	"fmt"

	"github.com/spf13/cobra"
)

var listCmd = &cobra.Command{
	Use:   "list (vector-databases | vector-dbs | vdbs | embeddings | embeds | vdb-embeds | collections | cols | vdb-cols) [VDB_NAME]",
	Short: "List vector database resources, embeddings, or collections",
	Long: `List vector database resources, embeddings, or collections.

Usage:
  maestro-k list vector-databases [options]
  maestro-k list vector-dbs [options]
  maestro-k list vdbs [options]
  maestro-k list embeddings VDB_NAME [options]
  maestro-k list embeds VDB_NAME [options]
  maestro-k list vdb-embeds VDB_NAME [options]
  maestro-k list collections VDB_NAME [options]
  maestro-k list cols VDB_NAME [options]
  maestro-k list vdb-cols VDB_NAME [options]

Examples:
  maestro-k list vector-dbs
  maestro-k list vector-databases --verbose
  maestro-k list vdbs --mcp-server-uri=http://localhost:8000
  maestro-k list embeddings my-database
  maestro-k list embeds my-database --verbose
  maestro-k list collections my-database
  maestro-k list cols my-database --verbose`,
	Args: cobra.MinimumNArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		resourceType := args[0]

		// Handle embeddings subcommand
		if resourceType == "embeddings" || resourceType == "embeds" || resourceType == "vdb-embeds" {
			if len(args) < 2 {
				return fmt.Errorf("VDB_NAME is required for embeddings command")
			}
			vdbName := args[1]
			return listEmbeddings(vdbName)
		}

		// Handle collections subcommand
		if resourceType == "collections" || resourceType == "cols" || resourceType == "vdb-cols" {
			if len(args) < 2 {
				return fmt.Errorf("VDB_NAME is required for collections command")
			}
			vdbName := args[1]
			return listCollections(vdbName)
		}

		// Validate resource type for vector databases
		if resourceType != "vector-databases" && resourceType != "vector-dbs" && resourceType != "vdbs" {
			return fmt.Errorf("unsupported resource type: %s. Use 'vector-databases', 'vector-dbs', 'vdbs', 'embeddings', 'embeds', 'vdb-embeds', 'collections', 'cols', or 'vdb-cols'", resourceType)
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

func listCollections(vdbName string) error {
	if verbose {
		fmt.Printf("Listing collections for vector database '%s'...\n", vdbName)
	}

	if dryRun {
		fmt.Printf("[DRY RUN] Would list collections for vector database '%s'\n", vdbName)
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

	// Call the MCP server to get collections with panic recovery
	var collectionsResult string
	var collectionsErr error

	func() {
		defer func() {
			if r := recover(); r != nil {
				// Convert panic to a user-friendly error
				collectionsErr = fmt.Errorf("MCP server could not be reached at %s. Please ensure the server is running and accessible", serverURI)
			}
		}()
		collectionsResult, collectionsErr = client.ListCollections(vdbName)
	}()

	if collectionsErr != nil {
		return fmt.Errorf("failed to get collections for vector database '%s': %w", vdbName, collectionsErr)
	}

	// Display results
	if !silent {
		fmt.Println(collectionsResult)
	}

	if verbose {
		fmt.Printf("Collections listing completed successfully for vector database '%s'\n", vdbName)
	}

	return nil
}
