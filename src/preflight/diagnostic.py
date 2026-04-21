"""
ARES-OS — Pre-flight Diagnostic Engine
Generates GO/NO-GO decision from hardware telemetry input.
"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class Decision(Enum):
    GO = "GO"
    NO_GO = "NO_GO"
    CAUTION = "CAUTION"

@dataclass
class DiagnosticResult:
    decision: Decision
    faults: List[str]
    warnings: List[str]
    confidence: float  # 0.0 – 1.0

class PreflightDiagnostic:
    # Thresholds
    RSSI_MIN = -85          # dBm
    VIDEO_LATENCY_MAX = 80  # ms
    BATTERY_CAPACITY_MIN = 0.80  # 80% rated capacity
    CELL_DELTA_MAX = 0.05   # V
    GPS_SATS_MIN = 8

    def run(self,
            rssi_dbm: float,
            video_latency_ms: float,
            battery_capacity_pct: float,
            cell_delta_v: float,
            gps_satellites: int,
            cycle_count: int,
            max_cycles: int = 150) -> DiagnosticResult:

        faults, warnings = [], []

        # Radio
        if rssi_dbm < self.RSSI_MIN:
            faults.append(f"Radio RSSI critical: {rssi_dbm} dBm (min {self.RSSI_MIN})")

        # Video
        if video_latency_ms > self.VIDEO_LATENCY_MAX:
            faults.append(f"Video latency too high: {video_latency_ms}ms (max {self.VIDEO_LATENCY_MAX}ms)")

        # Battery capacity
        if battery_capacity_pct < self.BATTERY_CAPACITY_MIN:
            faults.append(f"Battery degraded: {battery_capacity_pct:.0%} capacity (min 80%)")
        elif battery_capacity_pct < 0.90:
            warnings.append(f"Battery capacity low: {battery_capacity_pct:.0%}")

        # Cell delta
        if cell_delta_v > self.CELL_DELTA_MAX:
            faults.append(f"Cell imbalance detected: {cell_delta_v:.3f}V delta (max {self.CELL_DELTA_MAX}V)")

        # GPS
        if gps_satellites < self.GPS_SATS_MIN:
            warnings.append(f"GPS weak: {gps_satellites} satellites (recommended {self.GPS_SATS_MIN}+)")

        # Cycle count
        cycle_pct = cycle_count / max_cycles
        if cycle_pct > 1.0:
            faults.append(f"Battery over max cycles: {cycle_count}/{max_cycles}")
        elif cycle_pct > 0.85:
            warnings.append(f"Battery near end of life: {cycle_count}/{max_cycles} cycles")

        # Decision
        if faults:
            decision = Decision.NO_GO
        elif warnings:
            decision = Decision.CAUTION
        else:
            decision = Decision.GO

        confidence = 1.0 - (len(faults) * 0.25 + len(warnings) * 0.10)
        confidence = max(0.0, confidence)

        return DiagnosticResult(
            decision=decision,
            faults=faults,
            warnings=warnings,
            confidence=confidence
        )


# Example usage
if __name__ == "__main__":
    diag = PreflightDiagnostic()
    result = diag.run(
        rssi_dbm=-72,
        video_latency_ms=45,
        battery_capacity_pct=0.87,
        cell_delta_v=0.02,
        gps_satellites=11,
        cycle_count=120
    )
    print(f"Decision: {result.decision.value}")
    print(f"Faults:   {result.faults}")
    print(f"Warnings: {result.warnings}")
    print(f"Confidence: {result.confidence:.0%}")
