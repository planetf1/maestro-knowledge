# SPDX-License-Identifier: Apache 2.0
# Copyright (c) 2025 IBM

"""
Utility for on-demand memory debugging via process signals.
"""

import os
import tracemalloc
import signal
import time
import types


def _memory_dump_handler(signum: int, frame: types.FrameType | None) -> None:
    """
    Signal handler for SIGUSR1. Dumps memory allocation tracebacks.
    - If TRACEMALLOC_FILTER_PATTERN is set, it filters for that pattern.
    - Otherwise, it dumps the top 15 overall memory allocations.
    """
    print(f"Caught signal {signum} (SIGUSR1). Dumping memory allocation trace...")

    snapshot = tracemalloc.take_snapshot()

    # Allow filtering the trace via an environment variable
    filter_pattern = os.getenv("TRACEMALLOC_FILTER_PATTERN")

    if filter_pattern:
        print(f"Filtering for pattern: {filter_pattern}")
        file_filter = tracemalloc.Filter(True, filter_pattern)
        snapshot = snapshot.filter_traces((file_filter,))
        stats = snapshot.statistics("traceback")
        report_title = f"Memory Traceback for allocations matching '{filter_pattern}'"
        output_filename = f"memtrace-filtered-{time.strftime('%Y%m%d-%H%M%S')}.txt"
    else:
        print("No filter pattern set. Reporting top 15 memory allocations.")
        stats = snapshot.statistics("lineno")[:15]
        report_title = "Top 15 Memory Allocations by Line"
        output_filename = f"memtrace-top15-{time.strftime('%Y%m%d-%H%M%S')}.txt"

    output_path = os.path.join("/tmp", output_filename)

    try:
        with open(output_path, "w") as f:
            f.write(report_title + "\n")
            f.write("Triggered by SIGUSR1.\n")
            f.write("=" * 80 + "\n\n")

            if not stats:
                f.write("No matching allocations found in the current snapshot.\n")
            else:
                for i, stat in enumerate(stats):
                    f.write(f"--- Stat #{i + 1} ---\n")
                    f.write(f"{stat}\n")
                    # Full traceback is most useful when filtering
                    if filter_pattern:
                        f.write("Traceback (most recent call last):\n")
                        for line in stat.traceback.format():
                            f.write(f"  {line.strip()}\n")
                    f.write("\n")

        print(f"✅ Memory trace dump complete. Output written to: {output_path}")
    except Exception as e:
        print(f"❌ Failed to write memory trace dump: {e}")


def setup_memory_debugging() -> None:
    """
    Sets up a SIGUSR1 signal handler for on-demand memory debugging.

    This feature is only enabled if the ENABLE_TRACEMALLOC_DEBUG environment
    variable is set to a truthy value (e.g., 'true', '1', 'yes').
    """
    enable_tracemalloc = os.getenv("ENABLE_TRACEMALLOC_DEBUG", "false").lower() in (
        "true",
        "1",
        "yes",
    )

    if enable_tracemalloc:
        # Start tracing memory allocations. This is required for the handler to work.
        tracemalloc.start(25)

        # Register the handler for the SIGUSR1 signal
        signal.signal(signal.SIGUSR1, _memory_dump_handler)

        print(
            "💡 Memory dump handler registered for SIGUSR1. Use 'kill -SIGUSR1 <PID>' to trigger."
        )
        print(
            "   - Set TRACEMALLOC_FILTER_PATTERN to filter tracebacks (e.g., '*/anyio/*')."
        )
