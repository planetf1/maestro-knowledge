package main

import (
	"fmt"
	"strings"

	"github.com/spf13/cobra"
)

var (
	docLimit       int
	collectionName string
)

var queryCmd = &cobra.Command{
	Use:   "query",
	Short: "Query a vector database using the default query agent",
	Long: `Query a vector database using the default query agent.
	
This command allows you to ask questions about documents stored in a vector database.
The query agent will search through the documents and provide relevant answers.`,
	Example: `  maestro-k query my-vdb "What is the main topic of the documents?"
  maestro-k query my-vdb "Find information about API endpoints" --doc-limit 10`,
	Args: cobra.ExactArgs(2),
	RunE: func(cmd *cobra.Command, args []string) error {
		dbName := args[0]
		query := args[1]

		// Validate inputs
		if strings.TrimSpace(dbName) == "" {
			return fmt.Errorf("database name cannot be empty")
		}
		if strings.TrimSpace(query) == "" {
			return fmt.Errorf("query cannot be empty")
		}

		return queryVectorDatabase(dbName, query)
	},
}

var queryVdbCmd = &cobra.Command{
	Use:   "vdb",
	Short: "Query a vector database using the default query agent",
	Long: `Query a vector database using the default query agent.
	
This command allows you to ask questions about documents stored in a vector database.
The query agent will search through the documents and provide relevant answers.`,
	Example: `  maestro-k query vdb my-vdb "What is the main topic of the documents?"
  maestro-k query vdb my-vdb "Find information about API endpoints" --doc-limit 10`,
	Args: cobra.ExactArgs(2),
	RunE: func(cmd *cobra.Command, args []string) error {
		dbName := args[0]
		query := args[1]

		// Validate inputs
		if strings.TrimSpace(dbName) == "" {
			return fmt.Errorf("database name cannot be empty")
		}
		if strings.TrimSpace(query) == "" {
			return fmt.Errorf("query cannot be empty")
		}

		return queryVectorDatabase(dbName, query)
	},
}

func queryVectorDatabase(dbName, query string) error {
	if verbose {
		fmt.Println("Querying vector database...")
	}

	if dryRun {
		fmt.Println("[DRY RUN] Would query vector database")
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

	// Call the query method
	result, err := client.Query(dbName, query, docLimit, "Test_collection_lowercase")
	if err != nil {
		return fmt.Errorf("failed to query vector database: %w", err)
	}

	if !silent {
		fmt.Println("OK")
	}
	fmt.Println(result)
	return nil
}

func init() {
	// Add flags to query commands
	queryCmd.Flags().IntVarP(&docLimit, "doc-limit", "d", 5, "Maximum number of documents to consider")
	queryCmd.Flags().StringVarP(&collectionName, "collection-name", "c", "", "Collection name to search in")
	queryVdbCmd.Flags().IntVarP(&docLimit, "doc-limit", "d", 5, "Maximum number of documents to consider")
	queryVdbCmd.Flags().StringVarP(&collectionName, "collection-name", "c", "", "Collection name to search in")
}
