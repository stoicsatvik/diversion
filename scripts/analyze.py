#!/usr/bin/env python3
"""Conservative descriptive analysis of highway work-zone observations."""
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(name):
    with (ROOT / "data" / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def main():
    segments = load("segments.csv")
    observations = load("observations.csv")
    ids = [r["observation_id"] for r in observations]
    if len(ids) != len(set(ids)) or any(not x for x in ids):
        raise ValueError("Observation IDs must be nonempty and unique")
    segment_ids = {s["segment_id"] for s in segments}
    if any(o["segment_id"] not in segment_ids for o in observations):
        raise ValueError("Observation references an unknown segment")
    print(f"Segments: {len(segments)}; unique recorded objects: {len(observations)}")
    for s in segments:
        sid = s["segment_id"]
        obs = [o for o in observations if o["segment_id"] == sid]
        print(f"\n{sid}: {len(obs)} recorded objects")
        if s["coverage_complete"].strip().lower() != "yes":
            print("  Survey incomplete: density and rates withheld")
            continue
        try:
            length = float(s["length_km"])
        except (ValueError, TypeError):
            print("  Missing valid segment length: density withheld")
            continue
        if length <= 0:
            print("  Nonpositive segment length: density withheld")
            continue
        print(f"  Density: {len(obs)/length:.2f} objects/km")
        print(f"  Types: {dict(Counter(o['object_type'] for o in obs))}")
        assessed = [o for o in obs if o["condition"].strip().lower() in {"intact", "damaged"}]
        if assessed:
            damaged = sum(o["condition"].strip().lower() == "damaged" for o in assessed)
            print(f"  Damage among assessed objects: {damaged}/{len(assessed)} ({100*damaged/len(assessed):.1f}%)")
        else:
            print("  Damage rate: not available (no assessed conditions)")
    if not segments:
        print("No measured segments yet. Add real field observations to begin.")
if __name__ == "__main__":
    main()
