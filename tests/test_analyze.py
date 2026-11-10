"""Synthetic integrity checks; no field observations are invented."""
import unittest

from scripts.analyze import validate


class SurveyIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.segments = [{"segment_id": "s1", "coverage_complete": "yes", "length_km": "2"}]
        self.observations = [{
            "observation_id": "o1",
            "physical_object_id": "p1",
            "segment_id": "s1",
            "object_type": "sign",
            "condition": "",
        }]

    def test_valid_survey(self):
        validate(self.segments, self.observations)

    def test_duplicate_segments(self):
        with self.assertRaisesRegex(ValueError, "Segment IDs"):
            validate(self.segments * 2, self.observations)

    def test_blank_segment(self):
        with self.assertRaisesRegex(ValueError, "Segment IDs"):
            validate([dict(self.segments[0], segment_id=" ")], [])

    def test_duplicate_observation_ids(self):
        with self.assertRaisesRegex(ValueError, "Observation IDs"):
            validate(self.segments, self.observations * 2)

    def test_blank_physical_object_id(self):
        with self.assertRaisesRegex(ValueError, "Physical object IDs"):
            validate(self.segments, [dict(self.observations[0], physical_object_id=" ")])

    def test_same_physical_object_seen_in_multiple_images_must_not_be_counted_twice(self):
        second_view = dict(self.observations[0], observation_id="o2", evidence_file="second-photo.jpg")
        with self.assertRaisesRegex(ValueError, "Physical object IDs"):
            validate(self.segments, [self.observations[0], second_view])

    def test_missing_object_type(self):
        with self.assertRaisesRegex(ValueError, "Object type"):
            validate(self.segments, [dict(self.observations[0], object_type=" ")])

    def test_missing_condition_field(self):
        incomplete = {k: v for k, v in self.observations[0].items() if k != "condition"}
        with self.assertRaisesRegex(ValueError, "condition field"):
            validate(self.segments, [incomplete])

    def test_blank_condition_is_unknown(self):
        validate(self.segments, [dict(self.observations[0], condition="")])

    def test_unknown_segment(self):
        with self.assertRaisesRegex(ValueError, "unknown segment"):
            validate(self.segments, [dict(self.observations[0], segment_id="s2")])

    def test_invalid_complete_length(self):
        for length in ("", "0", "-1", "nan", "inf"):
            with self.subTest(length=length), self.assertRaises(ValueError):
                validate([dict(self.segments[0], length_km=length)], [])

    def test_incomplete_length_can_be_unknown(self):
        validate([dict(self.segments[0], coverage_complete="no", length_km="")], [])

    def test_observation_coordinates_must_be_paired(self):
        row = dict(self.observations[0], latitude="19.1")
        with self.assertRaisesRegex(ValueError, "supplied together"):
            validate(self.segments, [row])

    def test_observation_coordinate_ranges(self):
        for latitude, longitude in (("91", "72"), ("nan", "72"), ("19", "181"), ("19", "inf")):
            with self.subTest(latitude=latitude, longitude=longitude), self.assertRaises(ValueError):
                row = dict(self.observations[0], latitude=latitude, longitude=longitude)
                validate(self.segments, [row])

    def test_segment_endpoint_coordinates_must_be_paired(self):
        segment = dict(self.segments[0], start_lat="19.1")
        with self.assertRaisesRegex(ValueError, "supplied together"):
            validate([segment], self.observations)

    def test_segment_endpoint_coordinate_ranges(self):
        for latitude, longitude in (("-91", "72"), ("19", "181"), ("nan", "72")):
            with self.subTest(latitude=latitude, longitude=longitude), self.assertRaises(ValueError):
                segment = dict(self.segments[0], start_lat=latitude, start_lon=longitude)
                validate([segment], self.observations)

    def test_timestamp_must_be_iso8601_date_time(self):
        row = dict(self.observations[0], timestamp_local="yesterday")
        with self.assertRaisesRegex(ValueError, "ISO 8601"):
            validate(self.segments, [row])

    def test_valid_local_timestamp_and_video_offset(self):
        row = dict(
            self.observations[0],
            timestamp_local="2026-11-10T08:30:00+05:30",
            video_timestamp_s="12.5",
            latitude="19.123",
            longitude="72.987",
        )
        validate(self.segments, [row])

    def test_video_timestamp_must_be_finite_and_nonnegative(self):
        for value in ("nan", "inf", "-0.1"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                row = dict(self.observations[0], video_timestamp_s=value)
                validate(self.segments, [row])


if __name__ == "__main__":
    unittest.main()
