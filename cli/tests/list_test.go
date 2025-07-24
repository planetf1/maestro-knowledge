package main

import (
	"os/exec"
	"strings"
	"testing"
)

func TestListVectorDatabase(t *testing.T) {
	cmd := exec.Command("../../maestro-k", "list", "vector-db")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("List command failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !strings.Contains(outputStr, "No vector databases found") {
		t.Errorf("Expected 'No vector databases found' message, got: %s", outputStr)
	}
}

func TestListVectorDatabaseWithVerbose(t *testing.T) {
	cmd := exec.Command("../../maestro-k", "list", "vector-db", "--verbose")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("List command with verbose failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !strings.Contains(outputStr, "Listing vector databases") {
		t.Errorf("Expected verbose message 'Listing vector databases', got: %s", outputStr)
	}

	if !strings.Contains(outputStr, "Vector database listing logic would be implemented here") {
		t.Errorf("Expected verbose implementation message, got: %s", outputStr)
	}
}

func TestListVectorDatabaseWithInvalidResourceType(t *testing.T) {
	cmd := exec.Command("../../maestro-k", "list", "invalid-resource")
	output, err := cmd.CombinedOutput()

	// Should fail with invalid resource type
	if err == nil {
		t.Error("Expected command to fail with invalid resource type, but it succeeded")
	}

	outputStr := string(output)
	if !strings.Contains(outputStr, "unsupported resource type") {
		t.Errorf("Expected error about unsupported resource type, got: %s", outputStr)
	}
}

func TestListVectorDatabaseWithDryRun(t *testing.T) {
	cmd := exec.Command("../../maestro-k", "list", "vector-db", "--dry-run")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("List command with dry-run failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !strings.Contains(outputStr, "[DRY RUN] Would list vector databases") {
		t.Errorf("Expected dry-run message, got: %s", outputStr)
	}
}

func TestListVectorDatabaseWithSilent(t *testing.T) {
	cmd := exec.Command("../../maestro-k", "list", "vector-db", "--silent")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("List command with silent failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	// Should not contain the default "No vector databases found" message when silent
	if strings.Contains(outputStr, "No vector databases found") {
		t.Errorf("Should not show default message when silent, got: %s", outputStr)
	}
}

func TestListVectorDatabaseHelp(t *testing.T) {
	cmd := exec.Command("../../maestro-k", "list", "vector-db", "--help")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("List help command failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !strings.Contains(outputStr, "List vector database resources") {
		t.Errorf("Expected help message about listing vector databases, got: %s", outputStr)
	}

	if !strings.Contains(outputStr, "maestro-k list vector-db") {
		t.Errorf("Expected usage example, got: %s", outputStr)
	}
}

func TestListVectorDatabaseWithVectorDatabase(t *testing.T) {
	cmd := exec.Command("../../maestro-k", "list", "vector-database")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("List command with 'vector-database' failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !strings.Contains(outputStr, "No vector databases found") {
		t.Errorf("Expected 'No vector databases found' message, got: %s", outputStr)
	}
}

func TestListVectorDatabaseWithMultipleFlags(t *testing.T) {
	cmd := exec.Command("../../maestro-k", "list", "vector-db", "--verbose", "--dry-run")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("List command with multiple flags failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !strings.Contains(outputStr, "Listing vector databases") {
		t.Errorf("Expected verbose message, got: %s", outputStr)
	}

	if !strings.Contains(outputStr, "[DRY RUN] Would list vector databases") {
		t.Errorf("Expected dry-run message, got: %s", outputStr)
	}
}
