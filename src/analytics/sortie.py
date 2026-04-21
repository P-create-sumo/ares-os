"""
ARES-OS — Sortie Analytics Engine
Captures and analyzes mission outcomes over time.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
import statistics

@dataclass
class SortieRecord:
    sortie_id: str
    timestamp: str
    operator: str
    navigator: str
    mission_type: str          # strike / recon / logistics
    outcome: str               # hit / miss / abort / lost
    target_type: Optional[str]
    time_to_target_s: Optional[float]
    weather: str               # clear / overcast / rain / wind
    battery_pack_id: str
    notes: str = ""

class SortieAnalytics:
    def __init__(self, records: List[SortieRecord]):
        self.records = records

    def hit_rate(self, operator: Optional[str] = None) -> float:
        pool = [r for r in self.records if r.outcome in ("hit", "miss")]
        if operator:
            pool = [r for r in pool if r.operator == operator]
        if not pool:
            return 0.0
        return sum(1 for r in pool if r.outcome == "hit") / len(pool)

    def avg_time_to_target(self) -> Optional[float]:
        times = [r.time_to_target_s for r in self.records if r.time_to_target_s]
        return statistics.mean(times) if times else None

    def failure_breakdown(self) -> dict:
        aborts = sum(1 for r in self.records if r.outcome == "abort")
        lost = sum(1 for r in self.records if r.outcome == "lost")
        return {"aborts": aborts, "lost": lost, "total": len(self.records)}

    def report(self) -> dict:
        return {
            "total_sorties": len(self.records),
            "hit_rate": f"{self.hit_rate():.0%}",
            "avg_time_to_target_s": self.avg_time_to_target(),
            "failures": self.failure_breakdown()
        }
