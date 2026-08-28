#!/usr/bin/env python3
import os, shutil
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SRC = os.path.join(ROOT, "config", "board_override.json")
DST_DIR = os.path.join(ROOT, "data")
DST = os.path.join(DST_DIR, "board_override.json")
os.makedirs(DST_DIR, exist_ok=True)
if os.path.exists(SRC):
    shutil.copy2(SRC, DST)
    print("Copied", SRC, "->", DST)
else:
    print("No override file at", SRC, "- skipping copy.")
