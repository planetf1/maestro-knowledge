package main

import (
	"os"
	"os/exec"
	"strings"
	"testing"
)

func TestWriteDocument(t *testing.T) {
	// Create a temporary file for testing
	tempFile := createTempFile(t, "test-*.txt", "This is a test document content")
	defer os.Remove(tempFile)

	// Test cases
	testCases := []struct {
		name        string
		args        []string
		expectError bool
		errorMsg    string
	}{
		{
			name:        "write document with valid parameters",
			args:        []string{"write", "document", "test_local_milvus", "test_collection", "test_doc", "--file-name=" + tempFile, "--dry-run"},
			expectError: false,
		},
		{
			name:        "write document with non-existent database (dry-run succeeds)",
			args:        []string{"write", "document", "non_existent_db", "test_collection", "test_doc", "--file-name=" + tempFile, "--dry-run"},
			expectError: false, // Dry-run doesn't validate existence
		},
		{
			name:        "write document with non-existent collection (dry-run succeeds)",
			args:        []string{"write", "document", "test_local_milvus", "non_existent_collection", "test_doc", "--file-name=" + tempFile, "--dry-run"},
			expectError: false, // Dry-run doesn't validate existence
		},
		{
			name:        "write document with missing file name",
			args:        []string{"write", "document", "test_local_milvus", "test_collection", "test_doc", "--dry-run"},
			expectError: true,
			errorMsg:    "file name is required",
		},
		{
			name:        "write document with non-existent file",
			args:        []string{"write", "document", "test_local_milvus", "test_collection", "test_doc", "--file-name=nonexistent.txt", "--dry-run"},
			expectError: true,
			errorMsg:    "file not found",
		},
		{
			name:        "write document using vdb-doc alias",
			args:        []string{"write", "vdb-doc", "test_local_milvus", "test_collection", "test_doc", "--file-name=" + tempFile, "--dry-run"},
			expectError: false,
		},
		{
			name:        "write document using doc alias",
			args:        []string{"write", "doc", "test_local_milvus", "test_collection", "test_doc", "--file-name=" + tempFile, "--dry-run"},
			expectError: false,
		},
		{
			name:        "write document with embedding specified",
			args:        []string{"write", "document", "test_local_milvus", "test_collection", "test_doc", "--file-name=" + tempFile, "--embed=text-embedding-3-small", "--dry-run"},
			expectError: false,
		},
		{
			name:        "write document with doc-file-name flag",
			args:        []string{"write", "document", "test_local_milvus", "test_collection", "test_doc", "--doc-file-name=" + tempFile, "--dry-run"},
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

func TestWriteDocumentWithVerbose(t *testing.T) {
	// Create a temporary file for testing
	tempFile := createTempFile(t, "test-*.txt", "This is a test document content")
	defer os.Remove(tempFile)

	cmd := exec.Command("../maestro-k", "write", "document", "test_local_milvus", "test_collection", "test_doc", "--file-name="+tempFile, "--verbose", "--dry-run")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("Write command with verbose failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !strings.Contains(outputStr, "Writing document") {
		t.Errorf("Expected verbose message 'Writing document', got: %s", outputStr)
	}
	if !strings.Contains(outputStr, "[DRY RUN] Would write document") {
		t.Errorf("Expected dry-run message, got: %s", outputStr)
	}
}

func TestWriteDocumentWithSilent(t *testing.T) {
	// Create a temporary file for testing
	tempFile := createTempFile(t, "test-*.txt", "This is a test document content")
	defer os.Remove(tempFile)

	cmd := exec.Command("../maestro-k", "write", "document", "test_local_milvus", "test_collection", "test_doc", "--file-name="+tempFile, "--silent", "--dry-run")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("Write command with silent failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if strings.Contains(outputStr, "[DRY RUN] Would write document") {
		t.Error("Silent mode should not show dry-run message")
	}
}

func TestWriteDocumentHelp(t *testing.T) {
	cmd := exec.Command("../maestro-k", "write", "--help")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("Write help command failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !strings.Contains(outputStr, "Write vector database resources") {
		t.Errorf("Expected help message about writing vector database resources, got: %s", outputStr)
	}
}

func TestWriteDocumentSubcommandHelp(t *testing.T) {
	cmd := exec.Command("../maestro-k", "write", "document", "--help")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("Write document help command failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !strings.Contains(outputStr, "Write a document to a collection") {
		t.Errorf("Expected help message about writing documents, got: %s", outputStr)
	}
}

func TestWriteDocumentWithInvalidArguments(t *testing.T) {
	// Test cases for invalid arguments
	testCases := []struct {
		name        string
		args        []string
		expectError bool
		errorMsg    string
	}{
		{
			name:        "write document with missing arguments",
			args:        []string{"write", "document", "test_local_milvus", "test_collection"},
			expectError: true,
			errorMsg:    "accepts 3 arg(s), received 2",
		},
		{
			name:        "write document with too many arguments",
			args:        []string{"write", "document", "test_local_milvus", "test_collection", "test_doc", "extra_arg"},
			expectError: true,
			errorMsg:    "accepts 3 arg(s), received 4",
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
