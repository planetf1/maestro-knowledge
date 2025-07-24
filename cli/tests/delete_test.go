package main

import (
	"os/exec"
	"testing"
)

// TestDeleteVectorDatabase tests the delete vector-database command
func TestDeleteVectorDatabase(t *testing.T) {
	cmd := exec.Command("../../maestro-k", "delete", "vector-db", "test-db")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("Delete command failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !contains(outputStr, "✅ Vector database 'test-db' deleted successfully") {
		t.Errorf("Should show success message, got: %s", outputStr)
	}
}

// TestDeleteVectorDatabaseWithVerbose tests the delete command with verbose output
func TestDeleteVectorDatabaseWithVerbose(t *testing.T) {
	cmd := exec.Command("../../maestro-k", "delete", "vector-db", "test-db", "--verbose")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("Delete command failed with verbose: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !contains(outputStr, "Deleting vector database: test-db") {
		t.Errorf("Should show verbose output, got: %s", outputStr)
	}
	if !contains(outputStr, "✅ Vector database 'test-db' deleted successfully") {
		t.Errorf("Should show success message, got: %s", outputStr)
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
	cmd := exec.Command("../../maestro-k", "delete", "vector-db", "test-db", "--silent")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("Delete command failed with silent mode: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if contains(outputStr, "✅ Vector database 'test-db' deleted successfully") {
		t.Error("Silent mode should not show success message")
	}
}

// TestDeleteVectorDatabaseWithLongName tests with a long name
func TestDeleteVectorDatabaseWithLongName(t *testing.T) {
	longName := "very-long-vector-database-name-that-should-still-work"
	cmd := exec.Command("../../maestro-k", "delete", "vector-db", longName)
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("Delete command failed with long name: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !contains(outputStr, "✅ Vector database '"+longName+"' deleted successfully") {
		t.Errorf("Should show success message with long name, got: %s", outputStr)
	}
}

// TestDeleteVectorDatabaseWithSpecialCharacters tests with special characters in name
func TestDeleteVectorDatabaseWithSpecialCharacters(t *testing.T) {
	specialName := "test-db-with-special-chars_123"
	cmd := exec.Command("../../maestro-k", "delete", "vector-db", specialName)
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("Delete command failed with special characters: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !contains(outputStr, "✅ Vector database '"+specialName+"' deleted successfully") {
		t.Errorf("Should show success message with special characters, got: %s", outputStr)
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
