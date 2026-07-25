#!/bin/bash
# Wrapper around `shadcn add` that works around a CLI bug where
# components get written to a literal "./@" directory instead of
# resolving the @/ path alias to src/.

set -e

npx shadcn@latest add "$@"

if [ -d "./@" ]; then
  echo "Fixing misplaced shadcn output..."
  find ./@ -type f | while read -r file; do
    dest="src/${file#./@/}"
    mkdir -p "$(dirname "$dest")"
    if [ ! -f "$dest" ]; then
      mv "$file" "$dest"
      echo "  moved: $file -> $dest"
    else
      echo "  skipped (already exists): $dest"
    fi
  done
  rm -rf ./@
  echo "Done."
fi