#!/usr/bin/env bash
set -euo pipefail

FILE="lib/GaggiMateController/src/GaggiMateController.cpp"

if [ ! -f "$FILE" ]; then
  echo "ERROR: $FILE not found"
  exit 3
fi

echo "Working on $FILE"

# 1) Insert include if missing (after '#include <utility>')
if ! grep -q '#include "generated/board_override.h"' "$FILE"; then
  awk '{
    print;
    if ($0 ~ /#include <utility>/ && !added) { print "#include \"generated/board_override.h\""; added=1 }
  }' "$FILE" > "$FILE.tmp" && mv "$FILE.tmp" "$FILE"
  echo "Inserted include for generated/board_override.h"
else
  echo "Include already present"
fi

# 2) Replace the assignment if present (robust whitespace-aware regex)
if grep -q '_config[[:space:]]*=[[:space:]]*config[[:space:]]*;' "$FILE"; then
  # Use sed -E for extended regex; replace first occurrence in the detect block
  sed -E -i '0,/_config[[:space:]]*=[[:space:]]*config[[:space:]]*;/s//_config = applyBoardOverride(config);/' "$FILE"
  echo "Replaced _config = config; with _config = applyBoardOverride(config);"
else
  echo "Assignment pattern not found (already updated or different form)"
fi

# Diagnostics: show a small unified diff if the file changed
if git status --porcelain -- "$FILE" >/dev/null 2>&1; then
  if ! git diff --quiet -- "$FILE"; then
    echo "=== DIFF for $FILE ==="
    git --no-pager diff -- "$FILE"
  else
    echo "No content changes detected for $FILE"
  fi
fi
