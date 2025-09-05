package main

import (
    "os/exec"
    "strings"
    "testing"
)

func TestGetDocumentHelp(t *testing.T) {
    cmd := exec.Command("../maestro-k", "get-document", "--help")
    output, err := cmd.CombinedOutput()

    if err != nil {
        t.Fatalf("get-document help failed: %v, output: %s", err, string(output))
    }

    out := string(output)
    if !strings.Contains(out, "get-document") || !strings.Contains(out, "doc-name") {
        t.Errorf("help output should mention get-document and doc-name, got: %s", out)
    }
}

func TestGetDocumentDryRun(t *testing.T) {
    cmd := exec.Command("../maestro-k", "get-document", "my-doc", "--vdb=test_local_milvus", "--collection=test_collection", "--dry-run")
    output, err := cmd.CombinedOutput()

    if err != nil {
        t.Fatalf("get-document dry-run failed: %v, output: %s", err, string(output))
    }

    out := string(output)
    if !strings.Contains(out, "[DRY RUN]") || !strings.Contains(out, "Would get document 'my-doc'") {
        t.Errorf("dry-run output not as expected, got: %s", out)
    }
}

func TestGetDocumentMissingArgs(t *testing.T) {
    // Missing collection in non-interactive test mode should error
    cmd := exec.Command("../maestro-k", "get-document", "my-doc", "--vdb=test_local_milvus")
    output, err := cmd.CombinedOutput()

    if err == nil {
        t.Fatalf("expected error when collection missing in non-interactive mode, output: %s", string(output))
    }

    out := string(output)
    if !strings.Contains(out, "collection name is required in non-interactive mode") {
        t.Errorf("expected message about missing collection, got: %s", out)
    }
}
