#!/usr/bin/env python3
"""Conservative descriptive analysis of highway work-zone observations."""
import csv
from collections import Counter
from datetime import datetime
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    with (ROOT / "data" / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _optional_float(record, field, label):
    raw = record.get(field, "")
    text = "" if raw is None else str(raw).strip()
    if not text:
        return None
    try:
        value = float(text)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"{label} must be numeric") from exc
    if not math.isfinite(value):
        raise ValueError(f"{label} must be finite")
    return value


def _validate_coordinate_pair(record, latitude_field, longitude_field, label):
    latitude_text = str(record.get(latitude_field, "") or "").strip()
    longitude_text = str(record.get(longitude_field, "") or "").strip()
    if bool(latitude_text) != bool(longitude_text):
        raise ValueError(f"{label} latitude and longitude must be supplied together")
    if not latitude_text:
        return

    latitude = _optional_float(record, latitude_field, f"{label} latitude")
    longitude = _optional_float(record, longitude_field, f"{label} longitude")
    if not -90 <= latitude <= 90:
        raise ValueError(f"{label} latitude out of range")
    if not -180 <= longitude <= 180:
        raise ValueError(f"{label} longitude out of range")


def _validate_timestamp(record, field):
    raw = str(record.get(field, "") or "").strip()
    if not raw:
        return
    if "T" not in raw and " " not in raw:
        raise ValueError(f"{field} must be an ISO 8601 date-time")
    try:
        datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO 8601 date-time") from exc


def validate(segments, observations):
    """Reject malformed records before geospatial or rate calculations."""
    segment_ids = [s.get("segment_id", "").strip() for s in segments]
    if any(not x for x in segment_ids) or len(segment_ids) != len(set(segment_ids)):
        raise ValueError("Segment IDs must be nonempty and unique")
    segment_id_set = set(segment_ids)

    observation_ids = [o.get("observation_id", "").strip() for o in observations]
    if any(not x for x in observation_ids) or len(observation_ids) != len(set(observation_ids)):
        raise ValueError("Observation IDs must be nonempty and unique")

    physical_object_ids = [o.get("physical_object_id", "").strip() for o in observations]
    if any(not x for x in physical_object_ids) or len(physical_object_ids) != len(set(physical_object_ids)):
        raise ValueError("Physical object IDs must be nonempty and unique")

    for observation in observations:
        if observation.get("segment_id", "").strip() not in segment_id_set:
            raise ValueError("Observation references an unknown segment")
        if not observation.get("object_type", "").strip():
            raise ValueError("Object type must be nonempty")
        if "condition" not in observation or observation["condition"] is None:
            raise ValueError("Observation condition field is required; blank means unknown")

        _validate_coordinate_pair(observation, "latitude", "longitude", "Observation")
        _validate_timestamp(observation, "timestamp_local")
        video_time = _optional_float(observation, "video_timestamp_s", "Video timestamp")
        if video_time is not None and video_time < 0:
            raise ValueError("Video timestamp must be non-negative")

    for segment in segments:
        complete = segment.get("coverage_complete", "").strip().lower() == "yes"
        try:
            length = _optional_float(segment, "length_km", "Segment length")
        except ValueError as exc:
            if complete:
                raise ValueError("Complete segments require positive length_km") from exc
            raise
        if complete and (length is None or length <= 0):
            raise ValueError("Complete segments require positive length_km")
        if length is not None and length <= 0:
            raise ValueError("Segment length must be positive")

        _validate_coordinate_pair(segment, "start_lat", "start_lon", "Segment start")
        _validate_coordinate_pair(segment, "end_lat", "end_lon", "Segment end")


def main():
    segments = load("segments.csv")
    observations = load("observations.csv")
    validate(segments, observations)
    print(f"Segments: {len(segments)}; unique physical objects: {len(observations)}")
    for segment in segments:
        sid = segment["segment_id"]
        obs = [item for item in observations if item["segment_id"] == sid]
        print(f"\n{sid}: {len(obs)} unique physical objects")
        if segment["coverage_complete"].strip().lower() != "yes":
            print("  Survey incomplete: density and rates withheld")
            continue
        try:
            length = float(segment["length_km"])
        except (ValueError, TypeError):
            print("  Missing valid segment length: density withheld")
            continue
        if length <= 0:
            print("  Nonpositive segment length: density withheld")
            continue
        print(f"  Density: {len(obs)/length:.2f} objects/km")
        print(f"  Types: {dict(Counter(item['object_type'] for item in obs))}")
        assessed = [
            item for item in obs
            if item["condition"].strip().lower() in {"intact", "damaged"}
        ]
        if assessed:
            damaged = sum(item["condition"].strip().lower() == "damaged" for item in assessed)
            print(
                f"  Damage among assessed objects: {damaged}/{len(assessed)} "
                f"({100*damaged/len(assessed):.1f}%)"
            )
        else:
            print("  Damage rate: not available (no assessed conditions)")
    if not segments:
        print("No measured segments yet. Add real field observations to begin.")


if __name__ == "__main__":
    main()
