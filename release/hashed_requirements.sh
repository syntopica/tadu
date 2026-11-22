#!/bin/sh
# Prints a requirements file that pins tadu and every dependency by hash.
# The dependencies come from uv.lock; tadu itself from the distributions in dist/,
# so run it after `uv build`, on the files that are uploaded.
# Usage: release/hashed_requirements.sh [github]   (github adds the board's sign-in extra)
set -eu

version=$(uv version --short)
extra=${1:+--extra $1}
# shellcheck disable=SC2086 # $extra is empty or two words on purpose
uv export --frozen --no-default-groups $extra --no-emit-project --no-header --format requirements.txt
printf 'tadu==%s' "$version"
for file in dist/tadu-"$version"-py3-none-any.whl dist/tadu-"$version".tar.gz; do
  printf ' \\\n    --hash=sha256:%s' "$(sha256sum "$file" | cut -d' ' -f1)"
done
printf '\n'
