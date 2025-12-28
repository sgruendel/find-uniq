# find-uniq

Python utility to print paths from PRIMARY whose SHA256 isn't in OTHER files.

Input can be generated with commands like `find /some/dir -type f -exec sha256sum {} + > hashes.txt`
