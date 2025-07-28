package main

import (
	"fmt"
	"os"

	"github.com/joho/godotenv"
	"github.com/spf13/cobra"
)

var (
	version      = "0.1.0"
	buildTime    = "unknown"
	verbose      bool
	silent       bool
	dryRun       bool
	mcpServerURI string
)

func main() {
	// Load .env file if it exists
	if err := godotenv.Load(); err != nil {
		// .env file doesn't exist, which is fine
		// Only log error if it's not a "file not found" error
		if !os.IsNotExist(err) {
			fmt.Fprintf(os.Stderr, "Warning: Failed to load .env file: %v\n", err)
		}
	}

	var rootCmd = &cobra.Command{
		Use:   "maestro-k",
		Short: "Maestro Knowledge CLI tool",
		Long: `Maestro Knowledge CLI tool for validating YAML files and schemas.
		
A command-line interface for working with Maestro Knowledge configurations.`,
		Version: version + " (built " + buildTime + ")",
	}

	// Global flags
	rootCmd.PersistentFlags().BoolVarP(&verbose, "verbose", "", false, "Show all output")
	rootCmd.PersistentFlags().BoolVarP(&silent, "silent", "", false, "Show no additional output on success, e.g., no OK or Success etc")
	rootCmd.PersistentFlags().BoolVarP(&dryRun, "dry-run", "", false, "Mocks agents and other parts of workflow execution")
	rootCmd.PersistentFlags().StringVar(&mcpServerURI, "mcp-server-uri", "", "MCP server URI (overrides MAESTRO_KNOWLEDGE_MCP_SERVER_URI environment variable)")

	// Add commands
	rootCmd.AddCommand(validateCmd)
	rootCmd.AddCommand(createCmd)
	rootCmd.AddCommand(deleteCmd)
	rootCmd.AddCommand(listCmd)

	// Add sub-commands to create command
	createCmd.AddCommand(createVdbCmd)
	createCmd.AddCommand(createVdbShortCmd)
	createCmd.AddCommand(createVdbVdbCmd)
	createCmd.AddCommand(createCollectionCmd)
	createCmd.AddCommand(createVdbColCmd)
	createCmd.AddCommand(createColCmd)

	if err := rootCmd.Execute(); err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
}
