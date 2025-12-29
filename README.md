# find-uniq

Python utility to print paths from PRIMARY whose SHA256 isn't in OTHER files.

Input can be generated with commands like `fd -t f . /some/dir -x sha256sum > hashes.txt`
