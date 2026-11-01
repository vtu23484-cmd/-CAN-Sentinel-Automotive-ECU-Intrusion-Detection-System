"""Illustrative CAN-ID-to-signal mapping for synthetic demo traffic only."""
ECU_MAP = {
    0x100: "Engine ECU (RPM)",
    0x101: "Vehicle Dynamics ECU (speed)",
    0x102: "Thermal ECU (temperature)",
    0x180: "Brake Status ECU (simulated status only)",
    0x555: "Unknown / test node",
}

def describe(can_id: int) -> str:
    return ECU_MAP.get(int(can_id), "Unknown CAN ID")
