#!/usr/bin/env python3
"""
Generate src/generated/board_override.h from config/board_override.json.

Validation:
 - Detect duplicate pin assignments across output-capable fields and error.
 - Ensure I2C SCL != SDA.
 - Treat UART0 pins (1,3) as "unsafe"; fail unless allowUnsafe:true for that override.
 - Emits a helpful header comment with timestamp and the JSON used.
"""
import json
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "config" / "board_override.json"
OUT_DIR = ROOT / "src" / "generated"
OUT_FILE = OUT_DIR / "board_override.h"

# Output-capable fields (using push-pull or actively driven) to check duplicate output conflicts.
OUTPUT_FIELDS = {
    "heaterPin", "pumpPin", "valvePin", "altPin",
    "ext1Pin", "ext2Pin", "ext3Pin", "ext4Pin", "ext5Pin"
}

# "Unsafe" pins for ESP32-S3 we will warn/error about by default.
UNSAFE_PINS = {1, 3}

def load_json():
    if not JSON_PATH.exists():
        print(f"No {JSON_PATH} found: generating empty stub header.")
        return {"overrides": []}
    with JSON_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)

def validate_override(ov):
    errors = []
    warnings = []
    assigned = {}
    # collect assigned pins per logical field
    for key, val in ov.items():
        if key in ("autodetectValue", "name", "capabilities", "allowUnsafe"):
            continue
        if isinstance(val, int):
            assigned.setdefault(key, val)
    # Find duplicates among output-capable fields by pin number
    pin_to_fields = {}
    for field, pin in assigned.items():
        pin_to_fields.setdefault(pin, []).append(field)
    for pin, fields in pin_to_fields.items():
        outs = [f for f in fields if f in OUTPUT_FIELDS]
        if len(outs) > 1:
            errors.append(f"Pin {pin} assigned to multiple output fields: {outs}")
    # I2C SCL != SDA
    scl = ov.get("pressureScl")
    sda = ov.get("pressureSda")
    if scl is not None and sda is not None and scl == sda:
        errors.append(f"pressureScl and pressureSda are both {scl} (must be different)")
    # unsafe pins
    allow_unsafe = bool(ov.get("allowUnsafe"))
    used_unsafe = [pin for pin in pin_to_fields.keys() if pin in UNSAFE_PINS]
    if used_unsafe and not allow_unsafe:
        errors.append(f"Unsafe pins used: {used_unsafe}. Set allowUnsafe true to accept risk.")
    elif used_unsafe and allow_unsafe:
        warnings.append(f"Unsafe pins used but allowUnsafe=true: {used_unsafe} (you accept the risks)")
    return errors, warnings

def generate_header(data):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    lines = []
    lines.append("/*")
    lines.append("  Auto-generated board_override.h")
    lines.append(f"  Generated: {datetime.utcnow().isoformat()}Z")
    lines.append("  Source: config/board_override.json")
    lines.append("  NOTE: This file is generated - do not edit by hand.")
    lines.append("*/")
    lines.append("")
    lines.append("#pragma once")
    lines.append('#include "ControllerConfig.h"')
    lines.append("")
    lines.append("inline ControllerConfig applyBoardOverride(const ControllerConfig &base) {")
    lines.append("    ControllerConfig c = base;")
    overrides = data.get("overrides", [])
    for ov in overrides:
        adv = ov.get("autodetectValue")
        if adv is None:
            continue
        lines.append(f"    if (c.autodetectValue == {int(adv)}) {{")
        caps = ov.get("capabilities", {})
        for capk, capv in caps.items():
            vstr = "true" if capv else "false"
            # ControllerConfig uses the misspelled 'capabilites'
            lines.append(f'        c.capabilites.{capk} = {vstr};')
        for key, val in ov.items():
            if key in ("autodetectValue", "name", "capabilities", "allowUnsafe"):
                continue
            if isinstance(val, int):
                lines.append(f'        c.{key} = {val};')
        lines.append("        return c;")
        lines.append("    }")
    lines.append("    return c;")
    lines.append("}")
    OUT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_FILE}")

def main():
    data = load_json()
    overall_errors = []
    overall_warnings = []
    for ov in data.get("overrides", []):
        errs, warns = validate_override(ov)
        if errs:
            overall_errors.extend(errs)
        if warns:
            overall_warnings.extend(warns)
    if overall_warnings:
        print("Warnings:")
        for w in overall_warnings:
            print("  -", w)
    if overall_errors:
        print("Errors found in board_override.json:")
        for e in overall_errors:
            print("  -", e)
        print("Aborting generation. Fix the errors or set allowUnsafe:true where appropriate.")
        sys.exit(2)
    generate_header(data)
    print("Generation completed successfully.")

if __name__ == "__main__":
    main()
