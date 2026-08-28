#!/usr/bin/env python3
# PlatformIO pre-build extra script - runs the generator
import os, sys, subprocess
THIS_DIR = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(THIS_DIR, ".."))
GEN = os.path.join(ROOT, "scripts", "generate_board_override.py")
print("Running board override generator...")
ret = subprocess.call([sys.executable, GEN], cwd=ROOT)
if ret != 0:
    print("Generator failed with code", ret)
    sys.exit(ret)
print("Board override generation finished.")
