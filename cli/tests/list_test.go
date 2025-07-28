package main

import (
	"os/exec"
	"strings"
	"testing"
)

func TestListVectorDatabase(t *testing.T) {
	// Use dry-run mode since we don't have a real MCP server running
	cmd := exec.Command("../../maestro-k", "list", "vector-dbs", "--dry-run")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("List command failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !strings.Contains(outputStr, "[DRY RUN] Would list vector databases") {
		t.Errorf("Expected dry-run message, got: %s", outputStr)
	}
}

func TestListVectorDatabaseWithVerbose(t *testing.T) {
	// Use dry-run mode since we don't have a real MCP server running
	cmd := exec.Command("../../maestro-k", "list", "vector-dbs", "--verbose", "--dry-run")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("List command with verbose failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !strings.Contains(outputStr, "Listing vector databases") {
		t.Errorf("Expected verbose message 'Listing vector databases', got: %s", outputStr)
	}

	if !strings.Contains(outputStr, "[DRY RUN] Would list vector databases") {
		t.Errorf("Expected dry-run message, got: %s", outputStr)
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
	cmd := exec.Command("../../maestro-k", "list", "vector-dbs", "--dry-run")
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
	// Use dry-run mode since we don't have a real MCP server running
	cmd := exec.Command("../../maestro-k", "list", "vector-dbs", "--silent", "--dry-run")
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
	cmd := exec.Command("../../maestro-k", "list", "vector-dbs", "--help")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("List help command failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !strings.Contains(outputStr, "List vector database resources") {
		t.Errorf("Expected help message about listing vector databases, got: %s", outputStr)
	}

	if !strings.Contains(outputStr, "maestro-k list vector-dbs") {
		t.Errorf("Expected usage example, got: %s", outputStr)
	}
}

func TestListVectorDatabaseWithVectorDatabase(t *testing.T) {
	// Use dry-run mode since we don't have a real MCP server running
	cmd := exec.Command("../../maestro-k", "list", "vector-databases", "--dry-run")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("List command with 'vector-databases' failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !strings.Contains(outputStr, "[DRY RUN] Would list vector databases") {
		t.Errorf("Expected dry-run message, got: %s", outputStr)
	}
}

func TestListVectorDatabaseWithVdbShortcut(t *testing.T) {
	// Test with the "vdbs" shortcut
	cmd := exec.Command("../../maestro-k", "list", "vdbs", "--dry-run")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("List command with vdbs shortcut failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !strings.Contains(outputStr, "[DRY RUN] Would list vector databases") {
		t.Errorf("Expected dry-run message, got: %s", outputStr)
	}
}

func TestListVectorDatabaseWithMultipleFlags(t *testing.T) {
	cmd := exec.Command("../../maestro-k", "list", "vector-dbs", "--verbose", "--dry-run")
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

// TestListVectorDatabaseWithRealServer tests the actual MCP server connection
// This test is expected to fail if no MCP server is running, which is acceptable

func TestListEmbeddings(t *testing.T) {
	// Use dry-run mode since we don't have a real MCP server running
	cmd := exec.Command("../../maestro-k", "list", "embeddings", "test-db", "--dry-run")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("List embeddings command failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !strings.Contains(outputStr, "[DRY RUN] Would list embeddings for vector database 'test-db'") {
		t.Errorf("Expected dry-run message, got: %s", outputStr)
	}
}

func TestListEmbeddingsWithVerbose(t *testing.T) {
	// Use dry-run mode since we don't have a real MCP server running
	cmd := exec.Command("../../maestro-k", "list", "embeddings", "test-db", "--verbose", "--dry-run")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("List embeddings command with verbose failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !strings.Contains(outputStr, "Listing embeddings for vector database 'test-db'") {
		t.Errorf("Expected verbose message 'Listing embeddings for vector database 'test-db'', got: %s", outputStr)
	}

	if !strings.Contains(outputStr, "[DRY RUN] Would list embeddings for vector database 'test-db'") {
		t.Errorf("Expected dry-run message, got: %s", outputStr)
	}
}

func TestListEmbeddingsWithEmbedAlias(t *testing.T) {
	// Test the 'embeds' alias
	cmd := exec.Command("../../maestro-k", "list", "embeds", "test-db", "--dry-run")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("List embeds command failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !strings.Contains(outputStr, "[DRY RUN] Would list embeddings for vector database 'test-db'") {
		t.Errorf("Expected dry-run message, got: %s", outputStr)
	}
}

func TestListEmbeddingsWithVdbEmbedAlias(t *testing.T) {
	// Test the 'vdb-embeds' alias
	cmd := exec.Command("../../maestro-k", "list", "vdb-embeds", "test-db", "--dry-run")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("List vdb-embeds command failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !strings.Contains(outputStr, "[DRY RUN] Would list embeddings for vector database 'test-db'") {
		t.Errorf("Expected dry-run message, got: %s", outputStr)
	}
}

func TestListEmbeddingsMissingVdbName(t *testing.T) {
	cmd := exec.Command("../../maestro-k", "list", "embeddings")
	output, err := cmd.CombinedOutput()

	// Should fail with missing VDB_NAME
	if err == nil {
		t.Error("Expected command to fail with missing VDB_NAME, but it succeeded")
	}

	outputStr := string(output)
	if !strings.Contains(outputStr, "VDB_NAME is required for embeddings command") {
		t.Errorf("Expected error about missing VDB_NAME, got: %s", outputStr)
	}
}

func TestListEmbeddingsHelp(t *testing.T) {
	cmd := exec.Command("../../maestro-k", "list", "embeddings", "--help")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("List embeddings help command failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !strings.Contains(outputStr, "embeddings VDB_NAME") {
		t.Errorf("Expected help to mention embeddings VDB_NAME, got: %s", outputStr)
	}
}

func TestListCollections(t *testing.T) {
	// Use dry-run mode since we don't have a real MCP server running
	cmd := exec.Command("../../maestro-k", "list", "collections", "test-db", "--dry-run")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("List collections command failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !strings.Contains(outputStr, "[DRY RUN] Would list collections for vector database 'test-db'") {
		t.Errorf("Expected dry-run message, got: %s", outputStr)
	}
}

func TestListCollectionsWithVerbose(t *testing.T) {
	// Use dry-run mode since we don't have a real MCP server running
	cmd := exec.Command("../../maestro-k", "list", "collections", "test-db", "--verbose", "--dry-run")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("List collections command with verbose failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !strings.Contains(outputStr, "Listing collections for vector database 'test-db'") {
		t.Errorf("Expected verbose message 'Listing collections for vector database 'test-db'', got: %s", outputStr)
	}

	if !strings.Contains(outputStr, "[DRY RUN] Would list collections for vector database 'test-db'") {
		t.Errorf("Expected dry-run message, got: %s", outputStr)
	}
}

func TestListCollectionsWithColsAlias(t *testing.T) {
	// Test the 'cols' alias
	cmd := exec.Command("../../maestro-k", "list", "cols", "test-db", "--dry-run")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("List cols command failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !strings.Contains(outputStr, "[DRY RUN] Would list collections for vector database 'test-db'") {
		t.Errorf("Expected dry-run message, got: %s", outputStr)
	}
}

func TestListCollectionsWithVdbColsAlias(t *testing.T) {
	// Test the 'vdb-cols' alias
	cmd := exec.Command("../../maestro-k", "list", "vdb-cols", "test-db", "--dry-run")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("List vdb-cols command failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !strings.Contains(outputStr, "[DRY RUN] Would list collections for vector database 'test-db'") {
		t.Errorf("Expected dry-run message, got: %s", outputStr)
	}
}

func TestListCollectionsMissingVdbName(t *testing.T) {
	cmd := exec.Command("../../maestro-k", "list", "collections")
	output, err := cmd.CombinedOutput()

	// Should fail with missing VDB_NAME
	if err == nil {
		t.Error("Expected command to fail with missing VDB_NAME, but it succeeded")
	}

	outputStr := string(output)
	if !strings.Contains(outputStr, "VDB_NAME is required for collections command") {
		t.Errorf("Expected error about missing VDB_NAME, got: %s", outputStr)
	}
}

func TestListCollectionsHelp(t *testing.T) {
	cmd := exec.Command("../../maestro-k", "list", "collections", "--help")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("List collections help command failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !strings.Contains(outputStr, "collections VDB_NAME") {
		t.Errorf("Expected help to mention collections VDB_NAME, got: %s", outputStr)
	}
}

func TestListDocuments(t *testing.T) {
	// Use dry-run mode since we don't have a real MCP server running
	cmd := exec.Command("../../maestro-k", "list", "documents", "test-db", "test-collection", "--dry-run")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("List documents command failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !strings.Contains(outputStr, "[DRY RUN] Would list documents in collection 'test-collection' for vector database 'test-db'") {
		t.Errorf("Expected dry-run message, got: %s", outputStr)
	}
}

func TestListDocumentsWithVerbose(t *testing.T) {
	// Use dry-run mode since we don't have a real MCP server running
	cmd := exec.Command("../../maestro-k", "list", "documents", "test-db", "test-collection", "--verbose", "--dry-run")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("List documents command with verbose failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !strings.Contains(outputStr, "Listing documents in collection 'test-collection' for vector database 'test-db'") {
		t.Errorf("Expected verbose message 'Listing documents in collection 'test-collection' for vector database 'test-db'', got: %s", outputStr)
	}

	if !strings.Contains(outputStr, "[DRY RUN] Would list documents in collection 'test-collection' for vector database 'test-db'") {
		t.Errorf("Expected dry-run message, got: %s", outputStr)
	}
}

func TestListDocumentsWithDocsAlias(t *testing.T) {
	// Use dry-run mode since we don't have a real MCP server running
	cmd := exec.Command("../../maestro-k", "list", "docs", "test-db", "test-collection", "--dry-run")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("List documents command with docs alias failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !strings.Contains(outputStr, "[DRY RUN] Would list documents in collection 'test-collection' for vector database 'test-db'") {
		t.Errorf("Expected dry-run message, got: %s", outputStr)
	}
}

func TestListDocumentsWithVdbDocsAlias(t *testing.T) {
	// Use dry-run mode since we don't have a real MCP server running
	cmd := exec.Command("../../maestro-k", "list", "vdb-docs", "test-db", "test-collection", "--dry-run")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("List documents command with vdb-docs alias failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !strings.Contains(outputStr, "[DRY RUN] Would list documents in collection 'test-collection' for vector database 'test-db'") {
		t.Errorf("Expected dry-run message, got: %s", outputStr)
	}
}

func TestListDocumentsMissingVdbName(t *testing.T) {
	cmd := exec.Command("../../maestro-k", "list", "documents")
	output, err := cmd.CombinedOutput()

	// Should fail with missing VDB_NAME
	if err == nil {
		t.Error("Expected command to fail with missing VDB_NAME, but it succeeded")
	}

	outputStr := string(output)
	if !strings.Contains(outputStr, "VDB_NAME is required for documents command") {
		t.Errorf("Expected error about missing VDB_NAME, got: %s", outputStr)
	}
}

func TestListDocumentsMissingCollectionName(t *testing.T) {
	cmd := exec.Command("../../maestro-k", "list", "documents", "test-db")
	output, err := cmd.CombinedOutput()

	// Should fail with missing COLLECTION_NAME
	if err == nil {
		t.Error("Expected command to fail with missing COLLECTION_NAME, but it succeeded")
	}

	outputStr := string(output)
	if !strings.Contains(outputStr, "COLLECTION_NAME is required for documents command") {
		t.Errorf("Expected error about missing COLLECTION_NAME, got: %s", outputStr)
	}
}

func TestListDocumentsHelp(t *testing.T) {
	cmd := exec.Command("../../maestro-k", "list", "documents", "--help")
	output, err := cmd.CombinedOutput()

	if err != nil {
		t.Fatalf("List documents help command failed: %v, output: %s", err, string(output))
	}

	outputStr := string(output)
	if !strings.Contains(outputStr, "documents VDB_NAME COLLECTION_NAME") {
		t.Errorf("Expected help to mention documents VDB_NAME COLLECTION_NAME, got: %s", outputStr)
	}
}
