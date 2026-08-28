#!/usr/bin/env python3
"""
Generate src/generated/board_override.h and lib/GaggiMateController/src/generated/board_override.h
from config/board_override.json.
"""
import json, sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "config" / "board_override.json"
OUT_DIRS = [
    ROOT / "src" / "generated",
    ROOT / "lib" / "GaggiMateController" / "src" / "generated"
]

OUTPUT_FIELDS = {"heaterPin", "pumpPin", "valvePin", "altPin",
                 "ext1Pin", "ext2Pin", "ext3Pin", "ext4Pin", "ext5Pin"}
UNSAFE_PINS = {1, 3}

def load_json():
    if not JSON_PATH.exists():
        return {"overrides": []}
    return json.loads(JSON_PATH.read_text(encoding="utf-8"))

def validate_override(ov):
    errors = []
    warnings = []
    assigned = {}
    for key, val in ov.items():
        if key in ("autodetectValue", "name", "capabilities", "allowUnsafe"):
            continue
        if isinstance(val, int):
            assigned.setdefault(key, val)
    pin_to_fields = {}
    for field, pin in assigned.items():
        pin_to_fields.setdefault(pin, []).append(field)
    for pin, fields in pin_to_fields.items():
        outs = [f for f in fields if f in OUTPUT_FIELDS]
        if len(outs) > 1:
            errors.append(f"Pin {pin} assigned to multiple output fields: {outs}")
    scl = ov.get("pressureScl"); sda = ov.get("pressureSda")
    if scl is not None and sda is not None and scl == sda:
        errors.append(f"pressureScl and pressureSda are both {scl} (must be different)")
    allow_unsafe = bool(ov.get("allowUnsafe"))
    used_unsafe = [pin for pin in pin_to_fields.keys() if pin in UNSAFE_PINS]
    if used_unsafe and not allow_unsafe:
        errors.append(f"Unsafe pins used: {used_unsafe}. Set allowUnsafe true to accept risk.")
    elif used_unsafe and allow_unsafe:
        warnings.append(f"Unsafe pins used but allowUnsafe=true: {used_unsafe} (you accept the risks)")
    return errors, warnings

def build_contents(data):
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
    for ov in data.get("overrides", []):
        adv = ov.get("autodetectValue")
        if adv is None:
            continue
        lines.append(f"    if (c.autodetectValue == {int(adv)}) {{")
        caps = ov.get("capabilities", {})
        for capk, capv in caps.items():
            vstr = "true" if capv else "false"
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
    return "\n".join(lines) + "\n"

def main():
    data = load_json()
    errors = []; warnings = []
    for ov in data.get("overrides", []):
        e, w = validate_override(ov)
        errors.extend(e); warnings.extend(w)
    if warnings:
        print("Warnings:")
        for w in warnings: print(" -", w)
    if errors:
        print("Errors:")
        for e in errors: print(" -", e)
        print("Aborting generation.")
        sys.exit(2)
    content = build_contents(data)
    for d in OUT_DIRS:
        d.mkdir(parents=True, exist_ok=True)
        out_file = d / "board_override.h"
        out_file.write_text(content, encoding="utf-8")
        print("Wrote", out_file)

if __name__ == "__main__":
    main()
