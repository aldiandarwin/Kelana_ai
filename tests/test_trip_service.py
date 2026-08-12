"""Tests for the Session 2 trip recommendation rules."""

import unittest

from backend.services.trip_service import (
    calculate_daily_budget,
    get_recommended_places,
    get_travel_season,
    get_trip_category,
)


class TripServiceTests(unittest.TestCase):
    def test_trip_category_boundaries(self) -> None:
        cases = [
            (999, "Backpacker"),
            (1000, "Standard"),
            (3000, "Standard"),
            (3000.01, "Luxury"),
        ]

        for budget, expected in cases:
            with self.subTest(budget=budget):
                self.assertEqual(get_trip_category(budget), expected)

    def test_travel_season_rules(self) -> None:
        cases = [
            ("December", "Peak Season"),
            (" june ", "Holiday Season"),
            ("March", "Regular Season"),
        ]

        for month, expected in cases:
            with self.subTest(month=month):
                self.assertEqual(get_travel_season(month), expected)

    def test_daily_budget(self) -> None:
        self.assertEqual(calculate_daily_budget(1500, 5), 300)

    def test_zero_days_exposes_invalid_division(self) -> None:
        with self.assertRaises(ZeroDivisionError):
            calculate_daily_budget(1500, 0)

    def test_recommended_places_are_returned_as_a_list(self) -> None:
        self.assertEqual(
            get_recommended_places(),
            ["Tokyo Tower", "Shibuya", "Mount Fuji"],
        )

    def test_recommended_places_cannot_mutate_the_source_list(self) -> None:
        places = get_recommended_places()
        places.append("Osaka Castle")

        self.assertNotIn("Osaka Castle", get_recommended_places())


if __name__ == "__main__":
    unittest.main()
