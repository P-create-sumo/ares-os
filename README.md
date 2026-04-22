# ARES-OS v2.1 — Swarm Edition
**Free, open-source tactical C2 platform for FPV drone teams.**

Built from real battlefield reports. Solves pre-flight failures, disconnected roles, zero post-mission data.
Now with **Swarm Coordinator** — manages up to 50 UAVs with automated battery monitoring and reserve deployment.

## Live Demo
👉 [ares-os-app-7bb72773.base44.app](https://ares-os-app-7bb72773.base44.app)

## Pitch Deck
👉 [ares-os-app-7bb72773.base44.app/PitchDeck](https://ares-os-app-7bb72773.base44.app/PitchDeck)

## What it solves
- **No unified C2** — single interface for drones, missions, threats, intel
- **Zero situational awareness** — shared tactical picture between pilots, navigators, commanders
- **Manual pre-flight errors** — systematic GO/CAUTION/NO-GO checklist before launch
- **No post-mission data** — sortie outcomes, hit rates, operator performance captured and analyzed
- **Battery mismanagement** — cycle tracking, cell health monitoring, degraded pack flagging
- **Disconnected roles** — shared target marking, real-time coordination
- **No swarm management** — automated 50-UAV coordinator with coverage gap prevention

## Modules
| Module | Status | Description |
|--------|--------|-------------|
| Swarm Coordinator | ✅ Live | 50-UAV fleet management, auto RTB + reserve deploy |
| Pre-flight Wizard | ✅ Live | 6-parameter GO/CAUTION/NO-GO diagnostic |
| Battery Tracker | ✅ Live | Per-pack cycle count, capacity monitoring |
| Sortie Analytics | ✅ Live | Hit rate, failure breakdown, trend analysis |
| EW Monitor | 🔜 Roadmap | Jamming detection, frequency hop recommendation |
| Monte Carlo Sim | 🔜 Roadmap | Mission risk modeling, survival probability |

## Quick start
```bash
git clone https://github.com/P-create-sumo/ares-os
cd ares-os
pip install -r requirements.txt
python src/swarm/coordinator.py  # demo run
```

## License
MIT — free forever
