package main

import (
	"os/exec"
	"strings"
	"testing"
)

func TestRetrieveCollection(t *testing.T) {
	// Test cases
	testCases := []struct {
		name        string
		args        []string
		expectError bool
		errorMsg    string
	}{
		{
			name:        "retrieve collection with valid database",
			args:        []string{"retrieve", "collection", "test_local_milvus", "--dry-run"},
			expectError: false,
		},
		{
			name:        "retrieve collection with non-existent database (dry-run succeeds)",
			args:        []string{"retrieve", "collection", "non_existent_db", "--dry-run"},
			expectError: false, // Dry-run doesn't validate existence
		},
		{
			name:        "retrieve collection with specific collection name",
			args:        []string{"retrieve", "collection", "test_local_milvus", "test_collection", "--dry-run"},
			expectError: false,
		},
		{
			name:        "retrieve collection with invalid resource type",
			args:        []string{"retrieve", "invalid", "test_local_milvus", "--dry-run"},
			expectError: true,
			errorMsg:    "unsupported resource type",
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			cmd := exec.Command("../maestro-k", tc.args...)
			output, err := cmd.CombinedOutput()
			outputStr := string(output)

			if tc.expectError {
				if err == nil {
					t.Errorf("Expected error but command succeeded")
				}
				if tc.errorMsg != "" && !strings.Contains(outputStr, tc.errorMsg) {
					t.Errorf("Expected error message containing '%s', got: %s", tc.errorMsg, outputStr)
				}
			} else {
				if err != nil {
					t.Errorf("Unexpected error: %v, output: %s", err, outputStr)
				}
			}
		})
	}
}

func TestRetrieveDocument(t *testing.T) {
	// Test cases
	testCases := []struct {
		name        string
		args        []string
		expectError bool
		errorMsg    string
	}{
		{
			name:        "retrieve document with missing document name",
			args:        []string{"retrieve", "document", "test_local_milvus", "test_collection", "--dry-run"},
			expectError: true,
			errorMsg:    "collection name and document name are required",
		},
		{
			name:        "retrieve document with non-existent database (dry-run succeeds)",
			args:        []string{"retrieve", "document", "non_existent_db", "test_collection", "test_doc", "--dry-run"},
			expectError: false, // Dry-run doesn't validate existence
		},
		{
			name:        "retrieve document with non-existent collection (dry-run succeeds)",
			args:        []string{"retrieve", "document", "test_local_milvus", "non_existent_collection", "test_doc", "--dry-run"},
			expectError: false, // Dry-run doesn't validate existence
		},
		{
			name:        "retrieve document with non-existent document (dry-run succeeds)",
			args:        []string{"retrieve", "document", "test_local_milvus", "test_collection", "non_existent_doc", "--dry-run"},
			expectError: false, // Dry-run doesn't validate existence
		},
		{
			name:        "retrieve document with valid parameters",
			args:        []string{"retrieve", "document", "test_local_milvus", "test_collection", "test_document", "--dry-run"},
			expectError: false,
		},
		{
			name:        "retrieve document using vdb-doc alias",
			args:        []string{"retrieve", "vdb-doc", "test_local_milvus", "test_collection", "test_document", "--dry-run"},
			expectError: false,
		},
		{
			name:        "retrieve document using doc alias",
			args:        []string{"retrieve", "doc", "test_local_milvus", "test_collection", "test_document", "--dry-run"},
			expectError: false,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			cmd := exec.Command("../maestro-k", tc.args...)
			output, err := cmd.CombinedOutput()
			outputStr := string(output)

			if tc.expectError {
				if err == nil {
					t.Errorf("Expected error but command succeeded")
				}
				if tc.errorMsg != "" && !strings.Contains(outputStr, tc.errorMsg) {
					t.Errorf("Expected error message containing '%s', got: %s", tc.errorMsg, outputStr)
				}
			} else {
				if err != nil {
					t.Errorf("Unexpected error: %v, output: %s", err, outputStr)
				}
			}
		})
	}
}

func TestGetCollection(t *testing.T) {
	// Test cases
	testCases := []struct {
		name        string
		args        []string
		expectError bool
		errorMsg    string
	}{
		{
			name:        "get collection with valid database",
			args:        []string{"get", "collection", "test_local_milvus", "--dry-run"},
			expectError: false,
		},
		{
			name:        "get collection with non-existent database (dry-run succeeds)",
			args:        []string{"get", "collection", "non_existent_db", "--dry-run"},
			expectError: false, // Dry-run doesn't validate existence
		},
		{
			name:        "get collection with specific collection name",
			args:        []string{"get", "collection", "test_local_milvus", "test_collection", "--dry-run"},
			expectError: false,
		},
		{
			name:        "get collection using vdb-col alias",
			args:        []string{"get", "vdb-col", "test_local_milvus", "test_collection", "--dry-run"},
			expectError: false,
		},
		{
			name:        "get collection using col alias",
			args:        []string{"get", "col", "test_local_milvus", "test_collection", "--dry-run"},
			expectError: false,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			cmd := exec.Command("../maestro-k", tc.args...)
			output, err := cmd.CombinedOutput()
			outputStr := string(output)

			if tc.expectError {
				if err == nil {
					t.Errorf("Expected error but command succeeded")
				}
				if tc.errorMsg != "" && !strings.Contains(outputStr, tc.errorMsg) {
					t.Errorf("Expected error message containing '%s', got: %s", tc.errorMsg, outputStr)
				}
			} else {
				if err != nil {
					t.Errorf("Unexpected error: %v, output: %s", err, outputStr)
				}
			}
		})
	}
}

func TestGetDocument(t *testing.T) {
	// Test cases
	testCases := []struct {
		name        string
		args        []string
		expectError bool
		errorMsg    string
	}{
		{
			name:        "get document with missing document name",
			args:        []string{"get", "document", "test_local_milvus", "test_collection", "--dry-run"},
			expectError: true,
			errorMsg:    "collection name and document name are required",
		},
		{
			name:        "get document with non-existent database (dry-run succeeds)",
			args:        []string{"get", "document", "non_existent_db", "test_collection", "test_doc", "--dry-run"},
			expectError: false, // Dry-run doesn't validate existence
		},
		{
			name:        "get document with non-existent collection (dry-run succeeds)",
			args:        []string{"get", "document", "test_local_milvus", "non_existent_collection", "test_doc", "--dry-run"},
			expectError: false, // Dry-run doesn't validate existence
		},
		{
			name:        "get document with non-existent document (dry-run succeeds)",
			args:        []string{"get", "document", "test_local_milvus", "test_collection", "non_existent_doc", "--dry-run"},
			expectError: false, // Dry-run doesn't validate existence
		},
		{
			name:        "get document with valid parameters",
			args:        []string{"get", "document", "test_local_milvus", "test_collection", "test_document", "--dry-run"},
			expectError: false,
		},
		{
			name:        "get document using vdb-doc alias",
			args:        []string{"get", "vdb-doc", "test_local_milvus", "test_collection", "test_document", "--dry-run"},
			expectError: false,
		},
		{
			name:        "get document using doc alias",
			args:        []string{"get", "doc", "test_local_milvus", "test_collection", "test_document", "--dry-run"},
			expectError: false,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			cmd := exec.Command("../maestro-k", tc.args...)
			output, err := cmd.CombinedOutput()
			outputStr := string(output)

			if tc.expectError {
				if err == nil {
					t.Errorf("Expected error but command succeeded")
				}
				if tc.errorMsg != "" && !strings.Contains(outputStr, tc.errorMsg) {
					t.Errorf("Expected error message containing '%s', got: %s", tc.errorMsg, outputStr)
				}
			} else {
				if err != nil {
					t.Errorf("Unexpected error: %v, output: %s", err, outputStr)
				}
			}
		})
	}
}

func TestRetrieveVerboseMode(t *testing.T) {
	// Test verbose mode for retrieve collection
	cmd := exec.Command("../maestro-k", "retrieve", "collection", "test_local_milvus", "--verbose", "--dry-run")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("Retrieve command with verbose failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !strings.Contains(outputStr, "Retrieving collection information") {
		t.Errorf("Expected verbose output, got: %s", outputStr)
	}
}

func TestGetVerboseMode(t *testing.T) {
	// Test verbose mode for get document
	cmd := exec.Command("../maestro-k", "get", "document", "test_local_milvus", "test_collection", "test_document", "--verbose", "--dry-run")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("Get command with verbose failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !strings.Contains(outputStr, "Retrieving document information") {
		t.Errorf("Expected verbose output, got: %s", outputStr)
	}
}
