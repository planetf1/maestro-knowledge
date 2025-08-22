package main

import (
	"fmt"
	"strings"

	"github.com/spf13/cobra"
)

var diagnoseSearchCmd = &cobra.Command{
	Use:   "diagnose-search",
	Short: "Run a diagnostic search that returns embeddings and raw results",
	Long:  `Run a diagnostic search that returns the query embedding, collection info, and raw search results including _search_mode and scores.`,
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		query := args[0]
		vdbName, _ := cmd.Flags().GetString("vdb")
		collectionName, _ := cmd.Flags().GetString("collection")

		// Validate inputs
		if strings.TrimSpace(query) == "" {
			return fmt.Errorf("search cannot be empty")
		}

		// Use interactive selection if vdb name is not provided
		if vdbName == "" {
			var err error
			vdbName, err = PromptForVectorDatabase(vdbName)
			if err != nil {
				return fmt.Errorf("failed to select vector database: %w", err)
			}
		}

		// Use default collection if not specified
		if collectionName == "" {
			collectionName = "Test_collection_lowercase"
		}

		// Call the same internal function used by search but force diagnose=true
		return searchVectorDatabase(vdbName, query, collectionName, true)
	},
}

func init() {
	// Add flags similar to the regular search command
	diagnoseSearchCmd.Flags().String("vdb", "", "Vector database name")
	diagnoseSearchCmd.Flags().String("collection", "", "Collection name to search in")
	diagnoseSearchCmd.Flags().IntVarP(&docLimit, "doc-limit", "d", 5, "Maximum number of documents to consider")
}
