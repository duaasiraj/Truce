"""
run_tests.py

Runs all smoke tests sequentially.

Usage:
    python run_tests.py
"""

from importlib import import_module
from time import perf_counter
import traceback

TESTS = [
    ("Client Agent", "tests.test_client_agent"),
    ("Freelancer Agent", "tests.test_freelancer"),
    ("Mediator Agent", "tests.test_mediator"),
    ("Pipeline", "tests.test_pipeline"),
]


def banner(title: str):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def run_test(name: str, module_name: str):

    banner(f"RUNNING: {name}")

    start = perf_counter()

    try:
        module = import_module(module_name)

        if not hasattr(module, "main"):
            raise RuntimeError(
                f"{module_name} does not define a main() function."
            )

        module.main()

        elapsed = perf_counter() - start

        print(f"\n✅ {name} PASSED ({elapsed:.2f}s)\n")

        return True

    except Exception:

        elapsed = perf_counter() - start

        print(f"\n❌ {name} FAILED ({elapsed:.2f}s)\n")

        traceback.print_exc()

        return False


def main():

    banner("TRUCE BACKEND SMOKE TESTS")

    passed = 0

    failed = 0

    for name, module in TESTS:

        ok = run_test(name, module)

        if ok:
            passed += 1
        else:
            failed += 1

    banner("SUMMARY")

    print(f"Passed : {passed}")
    print(f"Failed : {failed}")
    print(f"Total  : {passed + failed}")

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED")
    else:
        print("\n⚠️ Some tests failed. Check the traceback above.")


if __name__ == "__main__":
    main()