package main

import (
	"os/exec"
	"testing"
)

// TestDeleteVectorDatabase tests the delete vector-database command
func TestDeleteVectorDatabase(t *testing.T) {
	cmd := exec.Command("../../maestro-k", "delete", "vector-db", "test-db", "--dry-run")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("Delete command failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !contains(outputStr, "[DRY RUN] Would delete vector database 'test-db'") {
		t.Errorf("Should show dry run message, got: %s", outputStr)
	}
}

// TestDeleteVectorDatabaseWithVerbose tests the delete command with verbose output
func TestDeleteVectorDatabaseWithVerbose(t *testing.T) {
	cmd := exec.Command("../../maestro-k", "delete", "vector-db", "test-db", "--verbose", "--dry-run")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("Delete command failed with verbose: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !contains(outputStr, "Deleting vector database: test-db") {
		t.Errorf("Should show verbose output, got: %s", outputStr)
	}
	if !contains(outputStr, "[DRY RUN] Would delete vector database 'test-db'") {
		t.Errorf("Should show dry run message, got: %s", outputStr)
	}
}

// TestDeleteVectorDatabaseWithInvalidResourceType tests invalid resource type
func TestDeleteVectorDatabaseWithInvalidResourceType(t *testing.T) {
	cmd := exec.Command("../../maestro-k", "delete", "invalid-resource", "test-db")
	output, err := cmd.CombinedOutput()

	// Should fail with invalid resource type
	if err == nil {
		t.Error("Delete command should fail with invalid resource type")
	}

	outputStr := string(output)
	if !contains(outputStr, "unsupported resource type") {
		t.Errorf("Error message should mention unsupported resource type, got: %s", outputStr)
	}
}

// TestDeleteVectorDatabaseWithEmptyName tests with empty name
func TestDeleteVectorDatabaseWithEmptyName(t *testing.T) {
	cmd := exec.Command("../../maestro-k", "delete", "vector-db", "")
	output, err := cmd.CombinedOutput()

	// Should fail with empty name
	if err == nil {
		t.Error("Delete command should fail with empty name")
	}

	outputStr := string(output)
	if !contains(outputStr, "vector database name is required") {
		t.Errorf("Error message should mention name is required, got: %s", outputStr)
	}
}

// TestDeleteVectorDatabaseDryRun tests dry run functionality
func TestDeleteVectorDatabaseDryRun(t *testing.T) {
	cmd := exec.Command("../../maestro-k", "delete", "vector-db", "test-db", "--dry-run")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("Delete command failed with dry run: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !contains(outputStr, "[DRY RUN] Would delete vector database 'test-db'") {
		t.Errorf("Should show dry run message, got: %s", outputStr)
	}
}

// TestDeleteVectorDatabaseSilent tests silent mode
func TestDeleteVectorDatabaseSilent(t *testing.T) {
	cmd := exec.Command("../../maestro-k", "delete", "vector-db", "test-db", "--silent", "--dry-run")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("Delete command failed with silent mode: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if contains(outputStr, "[DRY RUN] Would delete vector database 'test-db'") {
		t.Error("Silent mode should not show dry run message")
	}
}

// TestDeleteVectorDatabaseWithLongName tests with a long name
func TestDeleteVectorDatabaseWithLongName(t *testing.T) {
	longName := "very-long-vector-database-name-that-should-still-work"
	cmd := exec.Command("../../maestro-k", "delete", "vector-db", longName, "--dry-run")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("Delete command failed with long name: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !contains(outputStr, "[DRY RUN] Would delete vector database '"+longName+"'") {
		t.Errorf("Should show dry run message with long name, got: %s", outputStr)
	}
}

// TestDeleteVectorDatabaseWithSpecialCharacters tests with special characters in name
func TestDeleteVectorDatabaseWithSpecialCharacters(t *testing.T) {
	specialName := "test-db-with-special-chars_123"
	cmd := exec.Command("../../maestro-k", "delete", "vector-db", specialName, "--dry-run")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("Delete command failed with special characters: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !contains(outputStr, "[DRY RUN] Would delete vector database '"+specialName+"'") {
		t.Errorf("Should show dry run message with special characters, got: %s", outputStr)
	}
}

// TestDeleteVectorDatabaseWithVdbShortcut tests the delete command with vdb shortcut
func TestDeleteVectorDatabaseWithVdbShortcut(t *testing.T) {
	cmd := exec.Command("../../maestro-k", "delete", "vdb", "test-db", "--dry-run")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("Delete command with vdb shortcut failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !contains(outputStr, "[DRY RUN] Would delete vector database 'test-db'") {
		t.Errorf("Should show dry run message, got: %s", outputStr)
	}
}

// TestDeleteCollection tests the delete collection command
func TestDeleteCollection(t *testing.T) {
	cmd := exec.Command("../maestro-k", "delete", "collection", "test-db", "test-collection", "--dry-run")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("Delete collection command failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !contains(outputStr, "[DRY RUN] Would delete collection 'test-collection' from vector database 'test-db'") {
		t.Errorf("Should show dry run message, got: %s", outputStr)
	}
}

// TestDeleteCollectionWithVerbose tests the delete collection command with verbose output
func TestDeleteCollectionWithVerbose(t *testing.T) {
	cmd := exec.Command("../maestro-k", "delete", "collection", "test-db", "test-collection", "--verbose", "--dry-run")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("Delete collection command failed with verbose: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !contains(outputStr, "Deleting collection: test-collection from vector database: test-db") {
		t.Errorf("Should show verbose output, got: %s", outputStr)
	}
	if !contains(outputStr, "[DRY RUN] Would delete collection 'test-collection' from vector database 'test-db'") {
		t.Errorf("Should show dry run message, got: %s", outputStr)
	}
}

// TestDeleteCollectionWithInvalidResourceType tests invalid collection resource type
func TestDeleteCollectionWithInvalidResourceType(t *testing.T) {
	cmd := exec.Command("../maestro-k", "delete", "invalid-collection", "test-db", "test-collection")
	output, err := cmd.CombinedOutput()

	// Should fail with invalid resource type
	if err == nil {
		t.Error("Delete collection command should fail with invalid resource type")
	}

	outputStr := string(output)
	if !contains(outputStr, "unsupported resource type") {
		t.Errorf("Error message should mention unsupported resource type, got: %s", outputStr)
	}
}

// TestDeleteCollectionWithMissingCollectionName tests with missing collection name
func TestDeleteCollectionWithMissingCollectionName(t *testing.T) {
	cmd := exec.Command("../maestro-k", "delete", "collection", "test-db")
	output, err := cmd.CombinedOutput()

	// Should fail with missing collection name
	if err == nil {
		t.Error("Delete collection command should fail with missing collection name")
	}

	outputStr := string(output)
	if !contains(outputStr, "collection deletion requires both VDB_NAME and COLLECTION_NAME") {
		t.Errorf("Error message should mention missing collection name, got: %s", outputStr)
	}
}

// TestDeleteCollectionWithEmptyNames tests with empty names
func TestDeleteCollectionWithEmptyNames(t *testing.T) {
	cmd := exec.Command("../maestro-k", "delete", "collection", "", "test-collection")
	output, err := cmd.CombinedOutput()

	// Should fail with empty database name
	if err == nil {
		t.Error("Delete collection command should fail with empty database name")
	}

	outputStr := string(output)
	if !contains(outputStr, "vector database name is required") {
		t.Errorf("Error message should mention database name is required, got: %s", outputStr)
	}
}

// TestDeleteCollectionWithVdbColAlias tests the delete command with vdb-col alias
func TestDeleteCollectionWithVdbColAlias(t *testing.T) {
	cmd := exec.Command("../maestro-k", "delete", "vdb-col", "test-db", "test-collection", "--dry-run")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("Delete collection command with vdb-col alias failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !contains(outputStr, "[DRY RUN] Would delete collection 'test-collection' from vector database 'test-db'") {
		t.Errorf("Should show dry run message, got: %s", outputStr)
	}
}

// TestDeleteCollectionWithColAlias tests the delete command with col alias
func TestDeleteCollectionWithColAlias(t *testing.T) {
	cmd := exec.Command("../maestro-k", "delete", "col", "test-db", "test-collection", "--dry-run")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("Delete collection command with col alias failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !contains(outputStr, "[DRY RUN] Would delete collection 'test-collection' from vector database 'test-db'") {
		t.Errorf("Should show dry run message, got: %s", outputStr)
	}
}

// TestDeleteCollectionWithDelAlias tests the delete command with del alias
func TestDeleteCollectionWithDelAlias(t *testing.T) {
	cmd := exec.Command("../maestro-k", "del", "collection", "test-db", "test-collection", "--dry-run")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("Delete collection command with del alias failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !contains(outputStr, "[DRY RUN] Would delete collection 'test-collection' from vector database 'test-db'") {
		t.Errorf("Should show dry run message, got: %s", outputStr)
	}
}

// TestDeleteCollectionWithDelAliasAndMissingCollectionName tests del alias with missing collection name
func TestDeleteCollectionWithDelAliasAndMissingCollectionName(t *testing.T) {
	cmd := exec.Command("../maestro-k", "del", "collection", "test-db")
	output, err := cmd.CombinedOutput()

	// Should fail with missing collection name
	if err == nil {
		t.Error("Delete collection command with del alias should fail with missing collection name")
	}

	outputStr := string(output)
	if !contains(outputStr, "collection deletion requires both VDB_NAME and COLLECTION_NAME") {
		t.Errorf("Error message should mention missing collection name, got: %s", outputStr)
	}
}
