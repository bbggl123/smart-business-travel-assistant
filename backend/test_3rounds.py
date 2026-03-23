import asyncio
import sys
import subprocess
import os

os.environ['PYTHONPATH'] = os.path.dirname(os.path.abspath(__file__))

def run_pytest_round(round_num):
    print(f"\n{'='*70}")
    print(f"  FULL INTEGRATION TEST - ROUND {round_num}/3")
    print(f"{'='*70}")

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
        cwd=os.path.dirname(os.path.abspath(__file__)),
        capture_output=False
    )

    return result.returncode == 0

def main():
    print("\n" + "="*70)
    print("  MULTI-AGENT BUSINESS TRAVEL ASSISTANT - 3 ROUND SELF TEST")
    print("="*70)

    all_passed = True

    for round_num in range(1, 4):
        success = run_pytest_round(round_num)

        if not success:
            all_passed = False
            print(f"\n❌ ROUND {round_num} FAILED")
        else:
            print(f"\n✅ ROUND {round_num} PASSED")

    print("\n" + "="*70)
    if all_passed:
        print("  ✅✅✅ ALL 3 ROUNDS PASSED - READY FOR DELIVERY ✅✅✅")
    else:
        print("  ❌ SOME ROUNDS FAILED")
    print("="*70)

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
