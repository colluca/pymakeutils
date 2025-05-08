#!/usr/bin/env python3
#
# Author: Luca Colagrande

from anytree import Node, RenderTree
import argparse
import hashlib
from pathlib import Path
import re
import subprocess
import sys


# Parse arguments from the command line
def parse_args():
    parser = argparse.ArgumentParser(
        description="List prerequisites for a specified Makefile target.")
    parser.add_argument(
        'target',
        help="The make target whose prerequisites you want to list")
    parser.add_argument(
        '-r',
        '--recursive',
        action='store_true',
        help="Recursively list all prerequisites")
    parser.add_argument(
        '--hash',
        action='store_true',
        help="Generate a hash from the contents of all prerequisites")
    parser.add_argument(
        '-d',
        '--debug',
        action='store_true',
        help="Enable debug output to show intermediate steps")

    return parser.parse_args()


# Function to parse all rules from 'make -pq' output
def _parse_makefile():
    # Run 'make -pq' and capture its output
    result = subprocess.run(
        ['make', '-pq'],
        capture_output=True,
        text=True)

    # Initialize an empty dictionary to store the targets and their prerequisites
    targets = {}

    # Split the output by lines
    make_output = result.stdout.splitlines()

    # Regex to capture target and its prerequisites
    target_pattern = re.compile(r'^([^\s]+)\s*:\s*([^\|]*)')

    # Parse the make output
    for line in make_output:
        match = target_pattern.match(line)
        if match:
            target = match.group(1)
            prerequisites = match.group(2).split()
            targets[target] = prerequisites

    return targets


# Internal function used for recursion. Takes additional arguments to keep track of state.
def _get_prerequisites_recursive(target, targets, recursive=False):

    # Get the prerequisites for the target
    prerequisites = targets.get(target.name, [])

    # In non-recursive mode, attach prerequisites to root and that's it
    if not recursive:
        [Node(prereq, parent=target) for prereq in prerequisites]

    # In recursive mode, if we are at a leaf node, we return the leaf node
    # otherwise we attach the current prerequisite node to the parent
    else:

        if prerequisites:
            for prereq in prerequisites:

                # If recursive, get prerequisites for each prerequisite
                if recursive:
                    _get_prerequisites_recursive(
                        Node(prereq, parent=target),
                        targets,
                        recursive=True)
        else:
            return target


# Function to list prerequisites, optionally recursively
def list_prerequisites(target, recursive=False, debug=False):

    # Parse the makefile
    targets = _parse_makefile()

    # Get the prerequisites for the user-provided target, if it exists
    if target in targets:

        # Call the function with the user-provided target and recursive/debug flags
        root = Node(target)
        _get_prerequisites_recursive(
            root,
            targets,
            recursive=recursive)

        # Print tree structure for debugging
        if debug:
            for pre, fill, node in RenderTree(root):
                print(f"{pre}{node.name}")

            # Print a newline to separate debugging output from regular output
            print("")

        # Find all leaf prerequisites
        leaf_prerequisites = [node.name for node in root.descendants if node.is_leaf]

        # Remove repetitions and sort for consistency
        leaf_prerequisites = sorted(list(set(leaf_prerequisites)))

        # Return prerequisites
        return leaf_prerequisites

    else:
        raise Exception(f"Target '{args.target}' not found in the Makefile.")


def hash_files(file_list):
    # Create a new SHA-256 hash object
    hasher = hashlib.sha256()

    # If any prerequisite is a directory, replace it with its (recursive) contents
    expanded_file_list = []
    for file_name in file_list:
        file = Path(file_name)
        if file.is_dir():
            expanded_file_list.extend([str(f) for f in file.rglob('*') if f.is_file()])
        else:
            expanded_file_list.append(file_name)

    # Hash file contents
    for file_name in expanded_file_list:
        try:
            with open(file_name, 'rb') as f:
                # Read the file content in chunks to avoid memory issues with large files
                while chunk := f.read(8192):  # 8192 bytes per chunk
                    hasher.update(chunk)  # Update the hash with each chunk
        except FileNotFoundError:
            print(f"File '{file_name}' not found.", file=sys.stderr)

    # Return the final hexadecimal hash value
    return hasher.hexdigest()


if __name__ == "__main__":
    args = parse_args()

    prerequisites = list_prerequisites(args.target, recursive=args.recursive, debug=args.debug)

    if args.hash:
        # Print a hash of the prerequisites' contents
        hash_value = hash_files(prerequisites)
        print(hash_value)
    else:
        # Print the list of prerequisites
        print('\n'.join(prerequisites))
