"""Session 2: interactive Recommendation Engine for KelanaAI."""

from services.trip_service import (
    calculate_daily_budget,
    get_recommended_places,
    get_travel_season,
    get_trip_category,
)


def format_number(value: float) -> str:
    """Format a number without unnecessary decimal zeroes."""

    return f"{value:.2f}".rstrip("0").rstrip(".")


def print_trip_summary(
    destination: str,
    country: str,
    days: int,
    budget: float,
    currency: str,
    travel_month: str,
    category: str,
    daily_budget: float,
    season: str,
    recommended_places: list[str],
) -> None:
    """Print the trip details and recommendation results."""

    budget_text = format_number(budget)
    daily_budget_text = format_number(daily_budget)

    print("==================================")
    print("KelanaAI")
    print("==================================")
    print(f"Destination      : {destination}")
    print(f"Country          : {country}")
    print(f"Days             : {days}")
    print(f"Budget           : {budget_text} {currency}")
    print(f"Category         : {category}")
    print(f"Daily Budget     : {daily_budget_text} {currency}/Day")
    print(f"Travel Month     : {travel_month}")
    print(f"Season           : {season}")
    print()
    print("Recommended Places")

    for place in recommended_places:
        print(f"- {place}")


def main() -> None:
    """Collect trip details from the terminal and display the summary."""

    destination = input("Destination  : ").strip()
    country = input("Country      : ").strip()
    days = int(input("Days         : "))
    budget = float(input("Budget       : "))
    currency = input("Currency     : ").strip()
    travel_month = input("Travel Month : ").strip()

    category = get_trip_category(budget)
    daily_budget = calculate_daily_budget(budget, days)
    season = get_travel_season(travel_month)
    recommended_places = get_recommended_places()

    print()
    print_trip_summary(
        destination,
        country,
        days,
        budget,
        currency,
        travel_month,
        category,
        daily_budget,
        season,
        recommended_places,
    )


if __name__ == "__main__":
    main()
