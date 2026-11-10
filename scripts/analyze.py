#!/usr/bin/env python3
"""Conservative descriptive analysis of highway work-zone observations."""
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(name):
    with (ROOT / "data" / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def validate(segments, observations):
    """Reject malformed records before computing rates."""
    segment_ids = [s.get("segment_id", "").strip() for s in segments]
    if any(not x for x in segment_ids) or len(segment_ids) != len(set(segment_ids)):
        raise ValueError("Segment IDs must be nonempty and unique")
    observation_ids = [o.get("observation_id", "").strip() for o in observations]
    if any(not x for x in observation_ids) or len(observation_ids) != len(set(observation_ids)):
        raise ValueError("Observation IDs must be nonempty and unique")
    for o in observations:
        if o.get("segment_id", "").strip() not in set(segment_ids):
            raise ValueError("Observation references an unknown segment")
        if not o.get("object_type", "").strip():
            raise ValueError("Object type must be nonempty")
    for segment in segments:
        if segment.get("coverage_complete", "").strip().lower() == "yes":
            try:
                length = float(segment.get("length_km", ""))
            except (ValueError, TypeError):
                raise ValueError("Complete segments require positive length_km")
            if not (0 < length < float("inf")):
                raise ValueError("Complete segments require finite positive length_km")


def main():
    segments = load("segments.csv")
    observations = load("observations.csv")
    validate(segments, observations)
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
