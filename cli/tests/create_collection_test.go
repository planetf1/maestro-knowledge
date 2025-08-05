package main

import (
	"os/exec"
	"testing"
)

// TestCreateCollection tests the create collection command
func TestCreateCollection(t *testing.T) {
	cmd := exec.Command("../maestro-k", "collection", "create", "--name=test-collection", "--vdb=test-db", "--dry-run")
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
	cmd := exec.Command("../maestro-k", "collection", "create", "--name=test-collection", "--vdb=test-db", "--embedding=text-embedding-3-small", "--dry-run")
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
	cmd := exec.Command("../maestro-k", "collection", "create", "--name=test-collection", "--vdb=test-db", "--verbose", "--dry-run")
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
	cmd := exec.Command("../maestro-k", "collection", "create", "--name=test-collection", "--vdb=test-db", "--silent", "--dry-run")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("Create collection command failed with silent: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if contains(outputStr, "✅ Collection 'test-collection' created successfully") {
		t.Errorf("Should not show success message with silent flag, got: %s", outputStr)
	}
}

// TestCreateCollectionWithColAlias tests the create collection command using the collection command
func TestCreateCollectionWithColAlias(t *testing.T) {
	cmd := exec.Command("../maestro-k", "collection", "create", "--name=test-collection", "--vdb=test-db", "--dry-run")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("Create collection command failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !contains(outputStr, "[DRY RUN] Would create collection 'test-collection' in vector database 'test-db'") {
		t.Errorf("Should show dry run message, got: %s", outputStr)
	}
}

// TestCreateCollectionWithVdbColAlias tests the create collection command using the collection command
func TestCreateCollectionWithVdbColAlias(t *testing.T) {
	cmd := exec.Command("../maestro-k", "collection", "create", "--name=test-collection", "--vdb=test-db", "--dry-run")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("Create collection command failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !contains(outputStr, "[DRY RUN] Would create collection 'test-collection' in vector database 'test-db'") {
		t.Errorf("Should show dry run message, got: %s", outputStr)
	}
}

// TestCreateCollectionWithInvalidArgs tests the create collection command with invalid arguments
func TestCreateCollectionWithInvalidArgs(t *testing.T) {
	// Test with missing --name flag
	cmd := exec.Command("../maestro-k", "collection", "create", "--vdb=test-db")
	output, err := cmd.CombinedOutput()

	if err == nil {
		t.Errorf("Create collection command should fail with missing --name flag, got: %s", string(output))
	}

	// Test with missing --vdb flag
	cmd = exec.Command("../maestro-k", "collection", "create", "--name=test-collection")
	output, err = cmd.CombinedOutput()

	if err == nil {
		t.Errorf("Create collection command should fail with missing --vdb flag, got: %s", string(output))
	}
}

// TestCreateCollectionHelp tests the create collection help output
func TestCreateCollectionHelp(t *testing.T) {
	cmd := exec.Command("../maestro-k", "collection", "create", "--help")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("Create collection help command failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !contains(outputStr, "Create a collection") {
		t.Errorf("Should show help message for collection creation, got: %s", outputStr)
	}
	if !contains(outputStr, "--name string") {
		t.Errorf("Should show name flag in help, got: %s", outputStr)
	}
}
