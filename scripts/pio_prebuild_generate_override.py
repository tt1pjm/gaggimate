#!/usr/bin/env python3
# Helper for PlatformIO extra_scripts: run the generator before build
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT / "scripts" / "generate_board_override.py"

if not GEN.exists():
    print("Generator not found:", GEN)
    sys.exit(1)

ret = subprocess.run([sys.executable, str(GEN)], cwd=str(ROOT))
sys.exit(ret.returncode)
