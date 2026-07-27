"""Tests for the list-make-prerequisites and list-dependent-make-targets CLIs.

Both CLIs are exercised as subprocesses (rather than calling their `main()`
directly) so that the tests also cover argument parsing and console-script
wiring, running against the Makefile fixtures in this directory.
"""

import subprocess
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent


def run_cli(*args):
    result = subprocess.run(
        args, cwd=FIXTURES_DIR, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def test_list_prerequisites_non_recursive():
    assert run_cli('list-make-prerequisites', 'test1') == 'prereq'


def test_list_prerequisites_recursive():
    prerequisites = run_cli('list-make-prerequisites', 'test1', '--recursive').splitlines()
    assert prerequisites == ['preprereq1', 'preprereq2']


def test_hash_directory_prerequisite():
    hash_value = run_cli('list-make-prerequisites', 'test2', '--recursive', '--hash')
    assert hash_value == 'c64a77871513eadd52ec0e278bfbac1db866b77f66ebe91725b378b8bf43e29c'


def test_list_dependent_targets_non_recursive():
    assert run_cli('list-dependent-make-targets', 'preprereq1') == 'prereq'


def test_list_dependent_targets_recursive():
    targets = run_cli('list-dependent-make-targets', 'preprereq1', '--recursive').splitlines()
    assert targets == ['.DEFAULT_GOAL', 'prereq', 'test1']


def test_list_prerequisites_with_makecmdgoals_conditional_prerequisite():
    # `conditional`'s Makefile rule `-include`s a generated dependency file only when
    # `conditional` itself is passed as an actual Make goal (see test/Makefile). This
    # guards against a regression where the target was only used to look up its
    # prerequisites in a goal-less `make -pq` database dump, silently hiding any
    # prerequisite that depended on MAKECMDGOALS-conditional inclusion logic.
    prerequisites = run_cli('list-make-prerequisites', 'conditional', '--recursive').splitlines()
    assert prerequisites == ['hiddenprereq', 'standaloneprereq']
