package main

import (
	"fmt"

	"github.com/spf13/cobra"
)

var retrieveCmd = &cobra.Command{
	Use:   "retrieve (collection | vdb-col | col | document | vdb-doc | doc) VDB_NAME [COLLECTION_NAME]",
	Short: "Retrieve collection or document information from vector databases",
	Long: `Retrieve collection or document information from vector databases.

Usage:
  maestro-k retrieve collection VDB_NAME [COLLECTION_NAME] [options]
  maestro-k retrieve vdb-col VDB_NAME [COLLECTION_NAME] [options]
  maestro-k retrieve col VDB_NAME [COLLECTION_NAME] [options]
  maestro-k retrieve document VDB_NAME COLLECTION_NAME [options]
  maestro-k retrieve vdb-doc VDB_NAME COLLECTION_NAME [options]
  maestro-k retrieve doc VDB_NAME COLLECTION_NAME [options]

Examples:
  maestro-k retrieve collection my-database
  maestro-k retrieve col my-database my-collection --verbose
  maestro-k retrieve document my-database my-collection
  maestro-k retrieve doc my-database my-collection --verbose`,
	Args: cobra.MinimumNArgs(2),
	RunE: func(cmd *cobra.Command, args []string) error {
		resourceType := args[0]
		vdbName := args[1]

		// Handle collection subcommand
		if resourceType == "collection" || resourceType == "vdb-col" || resourceType == "col" {
			var collectionName string
			if len(args) > 2 {
				collectionName = args[2]
			}
			return retrieveCollection(vdbName, collectionName)
		}

		// Handle document subcommand
		if resourceType == "document" || resourceType == "vdb-doc" || resourceType == "doc" {
			if len(args) < 3 {
				return fmt.Errorf("COLLECTION_NAME is required for document command")
			}
			collectionName := args[2]
			return retrieveDocument(vdbName, collectionName)
		}

		return fmt.Errorf("unsupported resource type: %s. Use 'collection', 'vdb-col', 'col', 'document', 'vdb-doc', or 'doc'", resourceType)
	},
}

var getCmd = &cobra.Command{
	Use:   "get (collection | vdb-col | col | document | vdb-doc | doc) VDB_NAME [COLLECTION_NAME]",
	Short: "Get collection or document information from vector databases",
	Long: `Get collection or document information from vector databases.

Usage:
  maestro-k get collection VDB_NAME [COLLECTION_NAME] [options]
  maestro-k get vdb-col VDB_NAME [COLLECTION_NAME] [options]
  maestro-k get col VDB_NAME [COLLECTION_NAME] [options]
  maestro-k get document VDB_NAME COLLECTION_NAME [options]
  maestro-k get vdb-doc VDB_NAME COLLECTION_NAME [options]
  maestro-k get doc VDB_NAME COLLECTION_NAME [options]

Examples:
  maestro-k get collection my-database
  maestro-k get col my-database my-collection --verbose
  maestro-k get document my-database my-collection
  maestro-k get doc my-database my-collection --verbose`,
	Args: cobra.MinimumNArgs(2),
	RunE: func(cmd *cobra.Command, args []string) error {
		resourceType := args[0]
		vdbName := args[1]

		// Handle collection subcommand
		if resourceType == "collection" || resourceType == "vdb-col" || resourceType == "col" {
			var collectionName string
			if len(args) > 2 {
				collectionName = args[2]
			}
			return retrieveCollection(vdbName, collectionName)
		}

		// Handle document subcommand
		if resourceType == "document" || resourceType == "vdb-doc" || resourceType == "doc" {
			if len(args) < 3 {
				return fmt.Errorf("COLLECTION_NAME is required for document command")
			}
			collectionName := args[2]
			return retrieveDocument(vdbName, collectionName)
		}

		return fmt.Errorf("unsupported resource type: %s. Use 'collection', 'vdb-col', 'col', 'document', 'vdb-doc', or 'doc'", resourceType)
	},
}

func retrieveCollection(vdbName, collectionName string) error {
	if verbose {
		fmt.Println("Retrieving collection information...")
	}

	if dryRun {
		fmt.Println("[DRY RUN] Would retrieve collection information")
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

	// Call the get_collection_info method
	result, err := client.GetCollectionInfo(vdbName, collectionName)
	if err != nil {
		return fmt.Errorf("failed to retrieve collection info: %w", err)
	}

	if !silent {
		fmt.Println("OK")
	}
	fmt.Println(result)
	return nil
}

func retrieveDocument(vdbName, collectionName string) error {
	if verbose {
		fmt.Println("Retrieving document information...")
	}

	if dryRun {
		fmt.Println("[DRY RUN] Would retrieve document information")
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

	// For now, just list documents in the collection
	// TODO: Implement specific document retrieval
	result, err := client.ListDocumentsInCollection(vdbName, collectionName)
	if err != nil {
		return fmt.Errorf("failed to retrieve documents: %w", err)
	}

	if !silent {
		fmt.Println("OK")
	}
	fmt.Println(result)
	return nil
}
