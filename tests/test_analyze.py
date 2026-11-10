"""Synthetic integrity checks; no field observations are invented."""
import unittest
from scripts.analyze import validate


class SurveyIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.segments = [{"segment_id": "s1", "coverage_complete": "yes", "length_km": "2"}]
        self.observations = [{"observation_id": "o1", "segment_id": "s1", "object_type": "sign", "condition": ""}]

    def test_valid_survey(self):
        validate(self.segments, self.observations)

    def test_duplicate_segments(self):
        with self.assertRaisesRegex(ValueError, "Segment IDs"):
            validate(self.segments * 2, self.observations)

    def test_blank_segment(self):
        with self.assertRaisesRegex(ValueError, "Segment IDs"):
            validate([dict(self.segments[0], segment_id=" ")], [])

    def test_duplicate_objects(self):
        with self.assertRaisesRegex(ValueError, "Observation IDs"):
            validate(self.segments, self.observations * 2)

    def test_missing_object_type(self):
        with self.assertRaisesRegex(ValueError, "Object type"):
            validate(self.segments, [dict(self.observations[0], object_type=" ")])

    def test_missing_condition_field(self):
        with self.assertRaisesRegex(ValueError, "condition field"):
            validate(self.segments, [{k: v for k, v in self.observations[0].items() if k != "condition"}])

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


if __name__ == "__main__":
    unittest.main()
