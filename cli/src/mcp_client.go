package main

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"strings"
	"time"

	"github.com/joho/godotenv"
	"github.com/mark3labs/mcp-go/client"
	"github.com/mark3labs/mcp-go/mcp"
)

// MCPClient represents a client for interacting with the MCP server
type MCPClient struct {
	client  *client.Client
	baseURL string
	ctx     context.Context
}

// MCPResponse represents the response from the MCP server
type MCPResponse struct {
	JSONRPC string      `json:"jsonrpc"`
	ID      int         `json:"id"`
	Result  interface{} `json:"result,omitempty"`
	Error   *MCPError   `json:"error,omitempty"`
}

// MCPError represents an error from the MCP server
type MCPError struct {
	Code    int    `json:"code"`
	Message string `json:"message"`
}

// DatabaseInfo represents information about a vector database
type DatabaseInfo struct {
	Name          string `json:"name"`
	Type          string `json:"type"`
	Collection    string `json:"collection"`
	DocumentCount int    `json:"document_count"`
}

// normalizeURL ensures the URL has a protocol prefix and MCP endpoint
func normalizeURL(url string) string {
	// If it already has a protocol, just ensure it has the /mcp endpoint
	if strings.HasPrefix(url, "http://") || strings.HasPrefix(url, "https://") {
		if !strings.HasSuffix(url, "/mcp") {
			return strings.TrimSuffix(url, "/") + "/mcp"
		}
		return url
	}

	// If it's just a hostname:port, add http:// prefix and /mcp endpoint
	if strings.Contains(url, ":") {
		return "http://" + strings.TrimSuffix(url, "/") + "/mcp"
	}

	// If it's just a hostname, add http:// prefix, default port, and /mcp endpoint
	return "http://" + url + ":8030/mcp"
}

// getMCPServerURI gets the MCP server URI from environment variable or command line flag
func getMCPServerURI(cmdServerURI string) (string, error) {
	// Load .env file if it exists
	if _, err := os.Stat(".env"); err == nil {
		if err := godotenv.Load(); err != nil {
			return "", fmt.Errorf("failed to load .env file: %w", err)
		}
	}

	var serverURI string
	if cmdServerURI != "" {
		serverURI = cmdServerURI
	} else if envURI := os.Getenv("MAESTRO_KNOWLEDGE_MCP_SERVER_URI"); envURI != "" {
		serverURI = envURI
	} else {
		serverURI = "localhost:8030" // Default
	}

	return normalizeURL(serverURI), nil
}

// NewMCPClient creates a new MCP client
func NewMCPClient(serverURI string) (*MCPClient, error) {
	// Create context with timeout - use shorter timeout for tests
	timeout := 30 * time.Second
	if os.Getenv("MAESTRO_K_TEST_MODE") == "true" {
		timeout = 5 * time.Second // Shorter timeout for tests
	}
	ctx, _ := context.WithTimeout(context.Background(), timeout)

	// Create MCP client using HTTP transport
	// The mark3labs/mcp-go library supports HTTP transport for connecting to existing servers
	mcpClient, err := client.NewStreamableHttpClient(serverURI)
	if err != nil {
		// Provide user-friendly error messages for common connection issues
		errStr := err.Error()
		if strings.Contains(errStr, "connection refused") ||
			strings.Contains(errStr, "no such host") ||
			strings.Contains(errStr, "timeout") ||
			strings.Contains(errStr, "context deadline exceeded") ||
			strings.Contains(errStr, "network is unreachable") {
			return nil, fmt.Errorf("MCP server could not be reached at %s. Please ensure the server is running and accessible", serverURI)
		}
		return nil, fmt.Errorf("failed to create MCP client: %w", err)
	}

	return &MCPClient{
		client:  mcpClient,
		baseURL: serverURI,
		ctx:     ctx,
	}, nil
}

// callMCPServer makes a call to the MCP server using the mark3labs/mcp-go library
func (c *MCPClient) callMCPServer(method string, params interface{}) (*MCPResponse, error) {

	// Initialize the client if not already initialized
	if !c.client.IsInitialized() {
		initRequest := mcp.InitializeRequest{
			Request: mcp.Request{
				Method: "initialize",
			},
			Params: mcp.InitializeParams{
				ProtocolVersion: "2024-11-05",
				Capabilities:    mcp.ClientCapabilities{},
			},
		}

		_, err := c.client.Initialize(c.ctx, initRequest)
		if err != nil {
			// Provide user-friendly error messages for common connection issues
			errStr := err.Error()
			if strings.Contains(errStr, "connection refused") ||
				strings.Contains(errStr, "no such host") ||
				strings.Contains(errStr, "timeout") ||
				strings.Contains(errStr, "context deadline exceeded") ||
				strings.Contains(errStr, "network is unreachable") {
				return nil, fmt.Errorf("MCP server could not be reached at %s. Please ensure the server is running and accessible", c.baseURL)
			}
			return nil, fmt.Errorf("failed to initialize MCP client: %w", err)
		}
	}

	// Create the tool call request
	request := mcp.CallToolRequest{
		Request: mcp.Request{
			Method: method,
		},
		Params: mcp.CallToolParams{
			Name:      method,
			Arguments: params,
		},
	}

	// Call the tool
	response, err := c.client.CallTool(c.ctx, request)
	if err != nil {
		// Provide user-friendly error messages for common connection issues
		errStr := err.Error()
		if strings.Contains(errStr, "connection refused") ||
			strings.Contains(errStr, "no such host") ||
			strings.Contains(errStr, "timeout") ||
			strings.Contains(errStr, "context deadline exceeded") ||
			strings.Contains(errStr, "network is unreachable") {
			return nil, fmt.Errorf("MCP server could not be reached at %s. Please ensure the server is running and accessible", c.baseURL)
		}
		return nil, fmt.Errorf("failed to call MCP tool %s: %w", method, err)
	}

	// Convert the response to our format
	result := &MCPResponse{
		JSONRPC: "2.0",
		ID:      1,
	}

	// Extract the result from the response
	if response != nil && len(response.Content) > 0 {
		// Try to get text content
		if textContent, ok := mcp.AsTextContent(response.Content[0]); ok {
			// Try to parse as JSON first
			var jsonResult interface{}
			if err := json.Unmarshal([]byte(textContent.Text), &jsonResult); err == nil {
				result.Result = jsonResult
			} else {
				// If not JSON, use as string
				result.Result = textContent.Text
			}
		}
	}

	return result, nil
}

// ListDatabases calls the list_databases tool on the MCP server
func (c *MCPClient) ListDatabases() ([]DatabaseInfo, error) {
	response, err := c.callMCPServer("list_databases", nil)
	if err != nil {
		return nil, err
	}

	// The response structure depends on how the MCP server returns the result
	// We need to parse the result field which contains the JSON string
	if resultStr, ok := response.Result.(string); ok {
		// Check if it's a message indicating no databases
		if resultStr == "No vector databases are currently active" {
			return []DatabaseInfo{}, nil
		}

		// The result might be a formatted string like "Available vector databases:\n{JSON}"
		// Try to extract JSON from the string
		jsonStart := strings.Index(resultStr, "[")
		if jsonStart == -1 {
			jsonStart = strings.Index(resultStr, "{")
		}

		if jsonStart != -1 {
			jsonStr := resultStr[jsonStart:]
			var databases []DatabaseInfo
			if err := json.Unmarshal([]byte(jsonStr), &databases); err == nil {
				return databases, nil
			}
		}

		// If we can't extract JSON, try to parse the whole string as JSON
		var databases []DatabaseInfo
		if err := json.Unmarshal([]byte(resultStr), &databases); err != nil {
			return nil, fmt.Errorf("failed to parse database list: %w", err)
		}
		return databases, nil
	}

	return nil, fmt.Errorf("unexpected response format from MCP server")
}

// CreateVectorDatabase calls the create_vector_database_tool on the MCP server
func (c *MCPClient) CreateVectorDatabase(dbName, dbType, collectionName string) error {
	params := map[string]interface{}{
		"input": map[string]interface{}{
			"db_name":         dbName,
			"db_type":         dbType,
			"collection_name": collectionName,
		},
	}

	response, err := c.callMCPServer("create_vector_database_tool", params)
	if err != nil {
		return err
	}

	// The response should be a success message
	if response.Result == nil {
		return fmt.Errorf("no response from MCP server")
	}

	return nil
}

// SetupDatabase calls the setup_database tool on the MCP server
func (c *MCPClient) SetupDatabase(dbName, embedding string) error {
	params := map[string]interface{}{
		"input": map[string]interface{}{
			"db_name":   dbName,
			"embedding": embedding,
		},
	}

	response, err := c.callMCPServer("setup_database", params)
	if err != nil {
		return err
	}

	// The response should be a success message
	if response.Result == nil {
		return fmt.Errorf("no response from MCP server")
	}

	return nil
}

// DeleteVectorDatabase calls the cleanup tool on the MCP server
func (c *MCPClient) DeleteVectorDatabase(dbName string) error {
	params := map[string]interface{}{
		"input": map[string]interface{}{
			"db_name": dbName,
		},
	}

	response, err := c.callMCPServer("cleanup", params)
	if err != nil {
		return err
	}

	// The response should be a success message
	if response.Result == nil {
		return fmt.Errorf("no response from MCP server")
	}

	return nil
}

// Close closes the MCP client
func (c *MCPClient) Close() error {
	if c.client != nil {
		return c.client.Close()
	}
	return nil
}
