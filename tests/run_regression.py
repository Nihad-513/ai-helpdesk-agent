
import subprocess
import sys

TESTS = [
    "tests.test_retrieval_quality",
    "tests.test_retrieval_edge_cases",
    "tests.test_rag_responses",
    "tests.test_rag_followups",
]

for test in TESTS:
    print(f"\n{'=' * 70}")
    print(f"RUNNING: {test}")
    print("=" * 70)


    result = subprocess.run(
    [sys.executable, "-X", "utf8", "-m", test],
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace",
)

    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    if result.returncode != 0 or "RESULT: FAIL" in result.stdout:
        print(f"\nREGRESSION FAILED: {test}")
        sys.exit(1)

print("\nALL RAG REGRESSION SUITES PASSED.")
