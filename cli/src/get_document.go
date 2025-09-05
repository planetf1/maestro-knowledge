package main

import (
	"fmt"
	"strings"

	"github.com/spf13/cobra"
)

var getDocumentCmd = &cobra.Command{
	Use:   "get-document [doc-name]",
	Short: "Get a document from a collection",
	Long: `Get a document from a collection in a vector database.

	This command allows you to retrieve a document by its name from a specific collection.`,
	Example: `  maestro-k get-document "my-document" --vdb=my-vdb --collection=my-collection`,
	Args: cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		docName := args[0]
		vdbName, _ := cmd.Flags().GetString("vdb")
		collectionName, _ := cmd.Flags().GetString("collection")

		// Validate inputs
		if strings.TrimSpace(docName) == "" {
			return fmt.Errorf("document name cannot be empty")
		}

		// Use interactive selection if vdb name is not provided
		if vdbName == "" {
			var err error
			vdbName, err = PromptForVectorDatabase(vdbName)
			if err != nil {
				return fmt.Errorf("failed to select vector database: %w", err)
			}
		}

		// Use interactive selection if collection name is not provided
		if collectionName == "" {
			var err error
			collectionName, err = PromptForCollection(vdbName, collectionName)
			if err != nil {
				return fmt.Errorf("failed to select collection: %w", err)
			}
		}

		return getDocument(vdbName, collectionName, docName)
	},
}

func getDocument(dbName, collectionName, docName string) error {
	// Initialize progress indicator
	var progress *ProgressIndicator
	if ShouldShowProgress() {
		progress = NewProgressIndicator("Retrieving document...")
		progress.Start()
	}

	if verbose {
		fmt.Println("Retrieving document from vector database...")
	}

	if dryRun {
		if progress != nil {
			progress.Stop("Dry run completed")
		}
		fmt.Printf("[DRY RUN] Would get document '%s' from collection '%s' in vdb '%s'\n", docName, collectionName, dbName)
		return nil
	}

	if progress != nil {
		progress.Update("Connecting to MCP server...")
	}

	// Get MCP server URI
	serverURI, err := getMCPServerURI(mcpServerURI)
	if err != nil {
		if progress != nil {
			progress.StopWithError("Failed to get MCP server URI")
		}
		return fmt.Errorf("failed to get MCP server URI: %w", err)
	}

	if verbose {
		fmt.Printf("Connecting to MCP server at: %s\n", serverURI)
	}

	// Create MCP client
	client, err := NewMCPClient(serverURI)
	if err != nil {
		if progress != nil {
			progress.StopWithError("Failed to create MCP client")
		}
		return fmt.Errorf("failed to create MCP client: %w", err)
	}
	defer client.Close()

	if progress != nil {
		progress.Update("Retrieving document...")
	}

	// Call the get_document method
	result, err := client.GetDocument(dbName, collectionName, docName)
	if err != nil {
		if progress != nil {
			progress.StopWithError("Failed to retrieve document")
		}
		return fmt.Errorf("failed to get document: %w", err)
	}

	if progress != nil {
		progress.Stop("Document retrieved successfully")
	}

	if !silent {
		fmt.Println("OK")
	}
	fmt.Println(result)
	return nil
}

func init() {
	// Add flags to get-document command
	getDocumentCmd.Flags().String("vdb", "", "Vector database name")
	getDocumentCmd.Flags().String("collection", "", "Collection name")
}
