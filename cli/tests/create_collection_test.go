package main

import (
	"os/exec"
	"testing"
)

// TestCreateCollection tests the create collection command
func TestCreateCollection(t *testing.T) {
	cmd := exec.Command("../maestro-k", "create", "collection", "test-db", "test-collection", "--dry-run")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("Create collection command failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !contains(outputStr, "[DRY RUN] Would create collection 'test-collection' in vector database 'test-db'") {
		t.Errorf("Should show dry run message for collection creation, got: %s", outputStr)
	}
}

// TestCreateCollectionWithEmbedding tests the create collection command with custom embedding
func TestCreateCollectionWithEmbedding(t *testing.T) {
	cmd := exec.Command("../maestro-k", "create", "collection", "test-db", "test-collection", "--embedding=text-embedding-3-small", "--dry-run")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("Create collection command failed with embedding: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !contains(outputStr, "[DRY RUN] Would create collection 'test-collection' in vector database 'test-db' with embedding 'text-embedding-3-small'") {
		t.Errorf("Should show dry run message with custom embedding, got: %s", outputStr)
	}
}

// TestCreateCollectionWithVerbose tests the create collection command with verbose output
func TestCreateCollectionWithVerbose(t *testing.T) {
	cmd := exec.Command("../maestro-k", "create", "collection", "test-db", "test-collection", "--verbose", "--dry-run")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("Create collection command failed with verbose: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !contains(outputStr, "Creating collection 'test-collection' in vector database 'test-db'...") {
		t.Errorf("Should show verbose output, got: %s", outputStr)
	}
	if !contains(outputStr, "[DRY RUN] Would create collection 'test-collection' in vector database 'test-db'") {
		t.Errorf("Should show dry run message, got: %s", outputStr)
	}
}

// TestCreateCollectionWithSilent tests the create collection command with silent output
func TestCreateCollectionWithSilent(t *testing.T) {
	cmd := exec.Command("../maestro-k", "create", "collection", "test-db", "test-collection", "--silent", "--dry-run")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("Create collection command failed with silent: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if contains(outputStr, "✅ Collection 'test-collection' created successfully") {
		t.Errorf("Should not show success message with silent flag, got: %s", outputStr)
	}
}

// TestCreateCollectionWithColAlias tests the create collection command using the 'col' alias
func TestCreateCollectionWithColAlias(t *testing.T) {
	cmd := exec.Command("../maestro-k", "create", "col", "test-db", "test-collection", "--dry-run")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("Create collection command failed with col alias: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !contains(outputStr, "[DRY RUN] Would create collection 'test-collection' in vector database 'test-db'") {
		t.Errorf("Should show dry run message with col alias, got: %s", outputStr)
	}
}

// TestCreateCollectionWithVdbColAlias tests the create collection command using the 'vdb-col' alias
func TestCreateCollectionWithVdbColAlias(t *testing.T) {
	cmd := exec.Command("../maestro-k", "create", "vdb-col", "test-db", "test-collection", "--dry-run")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("Create collection command failed with vdb-col alias: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !contains(outputStr, "[DRY RUN] Would create collection 'test-collection' in vector database 'test-db'") {
		t.Errorf("Should show dry run message with vdb-col alias, got: %s", outputStr)
	}
}

// TestCreateCollectionWithInvalidArgs tests the create collection command with invalid arguments
func TestCreateCollectionWithInvalidArgs(t *testing.T) {
	// Test with missing arguments
	cmd := exec.Command("../maestro-k", "create", "collection", "test-db")
	output, err := cmd.CombinedOutput()

	if err == nil {
		t.Errorf("Create collection command should fail with missing arguments, got: %s", string(output))
	}

	// Test with too many arguments
	cmd = exec.Command("../maestro-k", "create", "collection", "test-db", "test-collection", "extra-arg")
	output, err = cmd.CombinedOutput()

	if err == nil {
		t.Errorf("Create collection command should fail with too many arguments, got: %s", string(output))
	}
}

// TestCreateCollectionHelp tests the create collection help output
func TestCreateCollectionHelp(t *testing.T) {
	cmd := exec.Command("../maestro-k", "create", "collection", "--help")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("Create collection help command failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !contains(outputStr, "Create a collection in a vector database") {
		t.Errorf("Should show help message for collection creation, got: %s", outputStr)
	}
	if !contains(outputStr, "--embedding string") {
		t.Errorf("Should show embedding flag in help, got: %s", outputStr)
	}
}
