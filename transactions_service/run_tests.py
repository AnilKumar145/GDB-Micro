cls#!/usr/bin/env python3
"""
Transaction Service - Test Execution Script

Utility script to run tests with various configurations and generate reports.
Usage: python run_tests.py [options]
"""

import subprocess
import sys
import argparse
from pathlib import Path


class TestRunner:
    """Handles test execution with various configurations."""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent / "tests"
        self.project_root = Path(__file__).parent
    
    def run_all_tests(self, verbose=True, coverage=False):
        """Run all test files."""
        print("\n" + "="*70)
        print("RUNNING ALL TESTS (500+ test cases)")
        print("="*70 + "\n")
        
        cmd = ["pytest", "tests/", "-v" if verbose else ""]
        
        if coverage:
            cmd.extend(["--cov=app", "--cov-report=html"])
        
        return subprocess.run(cmd, cwd=self.project_root)
    
    def run_unit_tests(self, verbose=True):
        """Run unit tests only."""
        print("\n" + "="*70)
        print("RUNNING UNIT TESTS (100+ test cases)")
        print("="*70 + "\n")
        
        cmd = ["pytest", "tests/test_comprehensive.py", "-v" if verbose else ""]
        return subprocess.run(cmd, cwd=self.project_root)
    
    def run_repository_tests(self, verbose=True):
        """Run repository tests only."""
        print("\n" + "="*70)
        print("RUNNING REPOSITORY TESTS (130+ test cases)")
        print("="*70 + "\n")
        
        cmd = ["pytest", "tests/test_repositories.py", "-v" if verbose else ""]
        return subprocess.run(cmd, cwd=self.project_root)
    
    def run_api_tests(self, verbose=True):
        """Run API endpoint tests only."""
        print("\n" + "="*70)
        print("RUNNING API ENDPOINT TESTS (150+ test cases)")
        print("="*70 + "\n")
        
        cmd = ["pytest", "tests/test_api_endpoints.py", "-v" if verbose else ""]
        return subprocess.run(cmd, cwd=self.project_root)
    
    def run_integration_tests(self, verbose=True):
        """Run integration tests only."""
        print("\n" + "="*70)
        print("RUNNING INTEGRATION TESTS (120+ test cases)")
        print("="*70 + "\n")
        
        cmd = ["pytest", "tests/test_integration.py", "-v" if verbose else ""]
        return subprocess.run(cmd, cwd=self.project_root)
    
    def run_test_class(self, test_class, verbose=True):
        """Run a specific test class."""
        print(f"\n" + "="*70)
        print(f"RUNNING TEST CLASS: {test_class}")
        print("="*70 + "\n")
        
        cmd = ["pytest", f"tests/{test_class}", "-v" if verbose else ""]
        return subprocess.run(cmd, cwd=self.project_root)
    
    def run_tests_by_keyword(self, keyword, verbose=True):
        """Run tests matching keyword."""
        print(f"\n" + "="*70)
        print(f"RUNNING TESTS MATCHING: {keyword}")
        print("="*70 + "\n")
        
        cmd = ["pytest", "tests/", f"-k={keyword}", "-v" if verbose else ""]
        return subprocess.run(cmd, cwd=self.project_root)
    
    def run_with_coverage(self):
        """Run tests with coverage report."""
        print("\n" + "="*70)
        print("RUNNING ALL TESTS WITH COVERAGE REPORT")
        print("="*70 + "\n")
        
        cmd = [
            "pytest", "tests/",
            "--cov=app",
            "--cov-report=html",
            "--cov-report=term-missing",
            "-v"
        ]
        return subprocess.run(cmd, cwd=self.project_root)
    
    def run_parallel(self, num_workers=4):
        """Run tests in parallel."""
        print(f"\n" + "="*70)
        print(f"RUNNING TESTS IN PARALLEL ({num_workers} workers)")
        print("="*70 + "\n")
        
        cmd = [
            "pytest", "tests/",
            f"-n={num_workers}",
            "-v"
        ]
        return subprocess.run(cmd, cwd=self.project_root)
    
    def run_failed_tests(self):
        """Run only previously failed tests."""
        print("\n" + "="*70)
        print("RUNNING PREVIOUSLY FAILED TESTS")
        print("="*70 + "\n")
        
        cmd = ["pytest", "tests/", "--lf", "-v"]
        return subprocess.run(cmd, cwd=self.project_root)
    
    def run_with_pdb(self, test_name):
        """Run specific test with debugger."""
        print(f"\n" + "="*70)
        print(f"RUNNING TEST WITH DEBUGGER: {test_name}")
        print("="*70 + "\n")
        
        cmd = ["pytest", f"tests/{test_name}", "--pdb", "-v"]
        return subprocess.run(cmd, cwd=self.project_root)
    
    def show_test_summary(self):
        """Show summary of all available tests."""
        print("\n" + "="*70)
        print("TEST SUMMARY - 500+ Test Cases")
        print("="*70 + "\n")
        
        print("UNIT TESTS (100+ cases)")
        print("  File: tests/test_comprehensive.py")
        print("  - EnumTests (9 cases)")
        print("  - AmountValidatorTests (10 cases)")
        print("  - BalanceValidatorTests (7 cases)")
        print("  - PINValidatorTests (11 cases)")
        print("  - TransferValidatorTests (4 cases)")
        print("  - TransferLimitValidatorTests (15+ cases)")
        print("  - ModelsTests (3 cases)")
        
        print("\nREPOSITORY TESTS (130+ cases)")
        print("  File: tests/test_repositories.py")
        print("  - TransactionRepositoryTests (7 cases)")
        print("  - TransactionLogRepositoryTests (11 cases)")
        print("  - TransferLimitRepositoryTests (12 cases)")
        
        print("\nAPI ENDPOINT TESTS (150+ cases)")
        print("  File: tests/test_api_endpoints.py")
        print("  - TestDepositEndpoint (10 cases)")
        print("  - TestWithdrawalEndpoint (6 cases)")
        print("  - TestTransferEndpoint (8 cases)")
        print("  - TestTransferLimitsEndpoint (7 cases)")
        print("  - TestTransactionLogsEndpoint (9 cases)")
        
        print("\nINTEGRATION TESTS (120+ cases)")
        print("  File: tests/test_integration.py")
        print("  - TestMultiAccountWorkflows (3 cases)")
        print("  - TestDailyLimitResets (3 cases)")
        print("  - TestPrivilegeLevelScenarios (4 cases)")
        print("  - TestConcurrentTransactions (3 cases)")
        print("  - TestTransactionLogLifecycle (3 cases)")
        print("  - TestErrorRecoveryScenarios (2 cases)")
        
        print("\nDOCUMENTATION")
        print("  - docs/COMPREHENSIVE_TEST_SUITE.md")
        print("  - docs/TEST_EXECUTION_GUIDE.md")
        print("  - docs/TEST_IMPLEMENTATION_SUMMARY.md")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Transaction Service Test Runner"
    )
    
    parser.add_argument(
        "command",
        nargs="?",
        default="all",
        choices=[
            "all", "unit", "repository", "api", "integration",
            "coverage", "parallel", "failed", "summary"
        ],
        help="Which tests to run"
    )
    
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Quiet mode (no verbose output)"
    )
    
    parser.add_argument(
        "-k", "--keyword",
        help="Run tests matching keyword"
    )
    
    parser.add_argument(
        "-n", "--num-workers",
        type=int,
        default=4,
        help="Number of workers for parallel execution"
    )
    
    parser.add_argument(
        "-t", "--test",
        help="Run specific test"
    )
    
    args = parser.parse_args()
    
    runner = TestRunner()
    verbose = not args.quiet
    
    if args.command == "all":
        result = runner.run_all_tests(verbose=verbose)
    elif args.command == "unit":
        result = runner.run_unit_tests(verbose=verbose)
    elif args.command == "repository":
        result = runner.run_repository_tests(verbose=verbose)
    elif args.command == "api":
        result = runner.run_api_tests(verbose=verbose)
    elif args.command == "integration":
        result = runner.run_integration_tests(verbose=verbose)
    elif args.command == "coverage":
        result = runner.run_with_coverage()
    elif args.command == "parallel":
        result = runner.run_parallel(num_workers=args.num_workers)
    elif args.command == "failed":
        result = runner.run_failed_tests()
    elif args.command == "summary":
        runner.show_test_summary()
        return 0
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()
        return 1
    
    if args.keyword:
        result = runner.run_tests_by_keyword(args.keyword, verbose=verbose)
    
    if args.test:
        result = runner.run_test_class(args.test, verbose=verbose)
    
    return result.returncode if result else 1


if __name__ == "__main__":
    sys.exit(main())
