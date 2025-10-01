# SPDX-License-Identifier: Apache 2.0
# Copyright (c) 2025 IBM

"""
Utility for on-demand memory debugging via process signals.
"""

import logging
import os
import tracemalloc
import signal
import time
import types

logger = logging.getLogger(__name__)


def _memory_dump_handler(signum: int, frame: types.FrameType | None) -> None:
    """
    Signal handler for SIGUSR1. Dumps memory allocation tracebacks to the logger.
    - If TRACEMALLOC_FILTER_PATTERN is set, it filters for that pattern.
    - Otherwise, it dumps the top 15 overall memory allocations.
    """
    logger.info(f"Caught signal {signum} (SIGUSR1). Dumping memory allocation trace...")

    snapshot = tracemalloc.take_snapshot()

    # Allow filtering the trace via an environment variable
    filter_pattern = os.getenv("TRACEMALLOC_FILTER_PATTERN")

    report_lines = []

    if filter_pattern:
        logger.info(f"Filtering for pattern: {filter_pattern}")
        file_filter = tracemalloc.Filter(True, filter_pattern)
        snapshot = snapshot.filter_traces((file_filter,))
        stats = snapshot.statistics("traceback")
        report_title = f"Memory Traceback for allocations matching '{filter_pattern}'"
    else:
        logger.info("No filter pattern set. Reporting top 15 memory allocations.")
        stats = snapshot.statistics("lineno")[:15]
        report_title = "Top 15 Memory Allocations by Line"

    report_lines.append("=" * 80)
    report_lines.append(report_title)
    report_lines.append(
        f"Triggered by SIGUSR1 at {time.strftime('%Y-%m-%d %H:%M:%S')}."
    )
    report_lines.append("=" * 80)

    if not stats:
        report_lines.append("No matching allocations found in the current snapshot.")
    else:
        for i, stat in enumerate(stats):
            report_lines.append(f"--- Stat #{i + 1} ---")
            report_lines.append(str(stat))
            # Full traceback is most useful when filtering
            if filter_pattern:
                report_lines.append("Traceback (most recent call last):")
                for line in stat.traceback.format():
                    report_lines.append(f"  {line.strip()}")
            report_lines.append("")

    report_lines.append("=" * 80)
    report_lines.append("End of memory trace dump.")
    report_lines.append("=" * 80)

    logger.info("\n".join(report_lines))


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
