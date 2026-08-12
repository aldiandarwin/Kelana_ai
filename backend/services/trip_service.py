"""Business rules for KelanaAI trip recommendations."""

RECOMMENDED_PLACES = [
    "Tokyo Tower",
    "Shibuya",
    "Mount Fuji",
]


def get_trip_category(budget: float) -> str:
    """Return a trip category based on the total budget."""

    if budget < 1000:
        return "Backpacker"
    elif budget <= 3000:
        return "Standard"
    else:
        return "Luxury"


def get_travel_season(month: str) -> str:
    """Return the travel season for the supplied month name."""

    normalized_month = month.strip().casefold()

    if normalized_month == "december":
        return "Peak Season"
    elif normalized_month == "june":
        return "Holiday Season"
    else:
        return "Regular Season"


def calculate_daily_budget(budget: float, days: int) -> float:
    """Divide the total budget across the number of travel days."""

    return budget / days


def get_recommended_places() -> list[str]:
    """Return the places recommended in the Session 2 assignment."""

    return RECOMMENDED_PLACES.copy()
