"""
ARES-OS — Battery Lifecycle Tracker
Tracks per-pack health, flags degraded units before deployment.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import uuid

@dataclass
class ChargeRecord:
    timestamp: str
    capacity_mah: float
    cell_delta_v: float
    cycle_number: int

@dataclass
class BatteryPack:
    pack_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8].upper())
    label: str = ""
    rated_capacity_mah: float = 1500.0
    max_cycles: int = 150
    charge_history: List[ChargeRecord] = field(default_factory=list)

    @property
    def cycle_count(self) -> int:
        return len(self.charge_history)

    @property
    def current_capacity_mah(self) -> float:
        if not self.charge_history:
            return self.rated_capacity_mah
        return self.charge_history[-1].capacity_mah

    @property
    def capacity_pct(self) -> float:
        return self.current_capacity_mah / self.rated_capacity_mah

    @property
    def is_serviceable(self) -> bool:
        return self.capacity_pct >= 0.80 and self.cycle_count <= self.max_cycles

    @property
    def health_status(self) -> str:
        if not self.is_serviceable:
            return "RETIRE"
        if self.capacity_pct < 0.90 or self.cycle_count > self.max_cycles * 0.85:
            return "CAUTION"
        return "OK"

    def log_charge(self, capacity_mah: float, cell_delta_v: float):
        self.charge_history.append(ChargeRecord(
            timestamp=datetime.utcnow().isoformat(),
            capacity_mah=capacity_mah,
            cell_delta_v=cell_delta_v,
            cycle_number=self.cycle_count + 1
        ))

    def summary(self) -> dict:
        return {
            "pack_id": self.pack_id,
            "label": self.label,
            "cycles": self.cycle_count,
            "capacity_pct": f"{self.capacity_pct:.0%}",
            "status": self.health_status
        }


if __name__ == "__main__":
    pack = BatteryPack(label="Pack-07", rated_capacity_mah=1500)
    pack.log_charge(1480, 0.01)
    pack.log_charge(1450, 0.02)
    pack.log_charge(1380, 0.03)
    print(pack.summary())
    print(f"Serviceable: {pack.is_serviceable}")
