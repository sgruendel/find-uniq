#!/usr/bin/env python3

"""Print paths from PRIMARY whose SHA256 isn't in OTHER files.

Usage:
	python3 find-uniq.py PRIMARY_HASHES_FILE OTHER_HASHES_FILE [OTHER2 ...]

Behavior:
	- Compares the PRIMARY file against one or more OTHER files (sha256sum format).
	- Prints paths from PRIMARY whose SHA256 value does not appear in any OTHER file.
	- Exposes utility functions: `load_hashes_set(path) -> set[sha]` and
		`get_files_by_sha(sha, mapping)`.

Input format:
	Lines in the form produced by `sha256sum`:
		<sha256><whitespace><path>
		
Input can be generated with commands like:
    - `find /some/dir -type f -exec sha256sum {} + > hashes.txt`
"""

import argparse
import fnmatch
import os
from typing import Dict, List, Set


def load_hashes_set(path: str) -> Set[str]:
	"""Load a file of sha256sum output and return a set of shas."""
	shas: Set[str] = set()
	with open(path, "r", encoding="utf-8") as f:
		for line in f:
			line = line.strip()
			if not line:
				continue
			parts = line.split(maxsplit=1)
			if not parts:
				continue
			shas.add(parts[0])
	return shas


def get_files_by_sha(sha: str, mapping: Dict[str, List[str]]) -> List[str]:
	return mapping.get(sha, [])


def print_unique_paths(
	primary_map: Dict[str, List[str]], other_shas: Set[str], ignore_patterns: List[str] | None = None
) -> None:
	"""Print paths from primary_map whose sha is not present in other_shas.

	Paths matching any pattern in `ignore_patterns` are skipped.
	"""
	ignore_patterns = ignore_patterns or []
	for sha, paths in primary_map.items():
		if sha in other_shas:
			continue
		for p in paths:
			# normalize path for matching
			norm = os.path.normpath(p)
			skip = False
			for pat in ignore_patterns:
				if fnmatch.fnmatch(norm, pat) or fnmatch.fnmatch(p, pat) or fnmatch.fnmatch(os.path.basename(p), pat):
					skip = True
					break
			if skip:
				continue
			print(p)


def process_primary_stream(primary_path: str, other_shas: Set[str], ignore_patterns: List[str] | None = None) -> None:
	"""Stream `primary_path` (sha256sum format) and print paths whose sha isn't in other_shas.

	This avoids building a full sha->paths mapping for the primary file.
	"""
	ignore_patterns = ignore_patterns or []
	with open(primary_path, "r", encoding="utf-8") as f:
		for line in f:
			line = line.strip()
			if not line:
				continue
			parts = line.split(maxsplit=1)
			if not parts:
				continue
			sha = parts[0]
			file_path = parts[1] if len(parts) > 1 else ""
			if sha in other_shas:
				continue
			norm = os.path.normpath(file_path)
			skip = False
			for pat in ignore_patterns:
				if fnmatch.fnmatch(norm, pat) or fnmatch.fnmatch(file_path, pat) or fnmatch.fnmatch(os.path.basename(file_path), pat):
					skip = True
					break
			if skip:
				continue
			print(file_path)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(
		prog="find-uniq.py",
		description="Print paths from PRIMARY whose SHA256 isn't in OTHER files",
	)
	parser.add_argument("primary", help="Primary hashes file (sha256sum format)")
	parser.add_argument("others", nargs="*", help="Other hashes files to compare against")
	parser.add_argument(
		"-i",
		"--ignore",
		action="append",
		default=[],
		help="Glob pattern to ignore (may be repeated), e.g. '**/desktop.ini'",
	)
	args = parser.parse_args()

	# Require at least one comparison file.
	if not args.others:
		parser.error("must provide at least one OTHER_HASHES_FILE to compare against")

	# Build combined set of SHAs from other files, then stream the primary file.
	other_shas: Set[str] = set()
	for fpath in args.others:
		other_shas.update(load_hashes_set(fpath))

	process_primary_stream(args.primary, other_shas, args.ignore)
