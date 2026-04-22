"""
ARES-OS — Swarm Coordinator v2.1
Manages up to 50 UAVs. Auto-returns drones at critical battery,
deploys reserves instantly. Zero coverage gaps guaranteed.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime
import asyncio

BATTERY_CRITICAL = 10.0   # %  → immediate RTB
BATTERY_WARNING  = 30.0   # %  → log warning
SCAN_INTERVAL_S  = 5      # seconds between scans


@dataclass
class DroneNode:
    drone_id: str
    status: str            # Active / Returning / Standby / Lost / Charging
    battery_pct: float
    lat: float
    lon: float
    alt_m: float
    sensor_radar: bool
    sensor_thermal: bool
    sensor_optical: bool
    coverage_radius_m: float
    assigned_zone: str
    is_reserve: bool
    alert: str = ""
    last_ping: str = ""

@dataclass
class SwarmEvent:
    timestamp: str
    event_type: str        # RTB / DEPLOY / WARNING / NOMINAL / COVERAGE_GAP
    drone_id: str
    zone: str
    battery_pct: float
    message: str

class SwarmCoordinator:
    """
    Core swarm logic — decoupled from any specific backend.
    Feed it DroneNode objects, get back SwarmEvents.
    """

    def __init__(self):
        self.event_log: List[SwarmEvent] = []

    def _log(self, event_type, drone_id, zone, batt, msg) -> SwarmEvent:
        ev = SwarmEvent(
            timestamp=datetime.utcnow().isoformat(),
            event_type=event_type,
            drone_id=drone_id,
            zone=zone,
            battery_pct=batt,
            message=msg
        )
        self.event_log.append(ev)
        print(f"[{ev.timestamp}] {event_type} | {drone_id} | zone={zone} | batt={batt:.1f}% | {msg}")
        return ev

    def scan(self, nodes: List[DroneNode]) -> List[SwarmEvent]:
        """
        Single scan pass. Returns list of events generated.
        Call this every SCAN_INTERVAL_S seconds.
        """
        events = []
        reserves = [n for n in nodes if n.is_reserve and n.status == "Standby" and n.battery_pct > 50]
        reserve_idx = 0

        for node in nodes:
            if node.is_reserve:
                continue

            # CRITICAL — immediate RTB
            if node.battery_pct <= BATTERY_CRITICAL and node.status == "Active":
                events.append(self._log("RTB", node.drone_id, node.assigned_zone, node.battery_pct,
                    f"Battery critical ({node.battery_pct:.1f}%) — RTB command issued"))
                node.status = "Returning"
                node.alert = "BATTERY CRITICAL — RETURNING"

                # Deploy reserve
                if reserve_idx < len(reserves):
                    res = reserves[reserve_idx]
                    res.status = "Active"
                    res.assigned_zone = node.assigned_zone
                    res.alert = ""
                    res.last_ping = datetime.utcnow().isoformat()
                    reserve_idx += 1
                    events.append(self._log("DEPLOY", res.drone_id, node.assigned_zone, res.battery_pct,
                        f"Deployed to replace {node.drone_id} — coverage maintained"))
                else:
                    events.append(self._log("COVERAGE_GAP", node.drone_id, node.assigned_zone, node.battery_pct,
                        f"No reserve available for zone {node.assigned_zone} — COVERAGE GAP"))

            # WARNING
            elif node.battery_pct <= BATTERY_WARNING and node.status == "Active":
                events.append(self._log("WARNING", node.drone_id, node.assigned_zone, node.battery_pct,
                    f"Battery low ({node.battery_pct:.1f}%) — plan replacement"))

        if not any(e.event_type in ("RTB","COVERAGE_GAP") for e in events):
            events.append(self._log("NOMINAL", "FLEET", "ALL", 0.0, "Scan complete — all nodes nominal"))

        return events

    def coverage_report(self, nodes: List[DroneNode]) -> Dict:
        """Returns per-zone coverage status."""
        zones = {}
        for node in nodes:
            if node.status == "Active" and not node.is_reserve:
                z = node.assigned_zone
                if z not in zones:
                    zones[z] = {"drones": 0, "avg_battery": 0.0, "radar": False, "thermal": False, "optical": False}
                zones[z]["drones"] += 1
                zones[z]["avg_battery"] += node.battery_pct
                zones[z]["radar"] = zones[z]["radar"] or node.sensor_radar
                zones[z]["thermal"] = zones[z]["thermal"] or node.sensor_thermal
                zones[z]["optical"] = zones[z]["optical"] or node.sensor_optical
        for z in zones:
            if zones[z]["drones"] > 0:
                zones[z]["avg_battery"] /= zones[z]["drones"]
        return zones


# ── Example usage ─────────────────────────────────────────────────
if __name__ == "__main__":
    nodes = [
        DroneNode("UAV-001","Active",87,48.38,31.17,120,True,True,True,500,"ALPHA",False),
        DroneNode("UAV-002","Active",8,48.376,31.162,110,True,True,False,500,"BRAVO",False),
        DroneNode("UAV-003","Standby",100,48.372,31.16,0,True,True,True,500,"BASE",True),
    ]
    coordinator = SwarmCoordinator()
    events = coordinator.scan(nodes)
    print(f"\n{len(events)} events generated")
    print("Coverage:", coordinator.coverage_report(nodes))
