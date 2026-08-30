#!/usr/bin/env bash
set -euo pipefail

FILE="lib/GaggiMateController/src/GaggiMateController.cpp"

if [ ! -f "$FILE" ]; then
  echo "ERROR: $FILE not found"
  exit 3
fi

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

# 2) Replace the assignment if present
if grep -q '_config = config;' "$FILE"; then
  sed -i 's/_config = config;/_config = applyBoardOverride(config);/' "$FILE"
  echo "Replaced _config = config; with applyBoardOverride(...)"
else
  echo "Assignment already updated or not present"
fi
