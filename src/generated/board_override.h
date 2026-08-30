/*
  Auto-generated board_override.h
  Generated: 2026-08-28T00:00:00Z
  Source: config/board_override.json
  NOTE: This file is generated - do not edit by hand.
*/

#pragma once
#include "ControllerConfig.h"

inline ControllerConfig applyBoardOverride(const ControllerConfig &base) {
    ControllerConfig c = base;
    if (c.autodetectValue == 1) {
        c.capabilites.dimming = true;
        c.capabilites.pressure = true;
        c.capabilites.ssrPump = false;
        c.capabilites.ledControls = false;
        c.capabilites.tof = false;
        c.pumpPin = 1;
        c.pumpSensePin = 2;
        c.pressureScl = 8;
        c.pressureSda = 12;
        return c;
    }
    return c;
}
