import re


def parse_log(log: str) -> dict[str, str]:
    """Parse test runner output into per-test results.

    Args:
        log: Full stdout+stderr output of `bash run_test.sh 2>&1`.

    Returns:
        Dict mapping test_id to status.
        - test_id: pytest native format (e.g. "tests/foo.py::TestClass::test_func")
        - status: one of "PASSED", "FAILED", "SKIPPED", "ERROR"
        - Must include ALL tests that appear in the output, not just failures.
    """
    results = {}
    # Strip ANSI escape codes
    log = re.sub(r'\x1b\[[0-9;]*m', '', log)

    for line in log.splitlines():
        line = line.strip()

        # pytest verbose output: "tests/test_smoke.py::TestClass::test_func PASSED [ 50%]"
        m = re.match(
            r'^(\S+::\S+.*?)\s+(PASSED|FAILED|SKIPPED|ERROR)(?:\s.*)?$',
            line
        )
        if m:
            test_id = m.group(1)
            status = m.group(2)
            results.setdefault(test_id, status)
            continue

        # Handle collection errors: "ERROR tests/foo.py" (no ::)
        m = re.match(r'^ERROR\s+(tests/\S+\.py)\s*', line)
        if m:
            test_id = m.group(1)
            results.setdefault(test_id, "ERROR")
            continue

    return results

