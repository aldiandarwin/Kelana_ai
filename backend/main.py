"""Session 1: interactive Trip Summary Generator for KelanaAI."""


def print_trip_summary(
    destination: str,
    country: str,
    days: int,
    budget: float,
    currency: str,
    travel_month: str,
) -> None:
    """Print a structured summary of the user's trip."""

    budget_text = f"{budget:.2f}".rstrip("0").rstrip(".")

    print("========================")
    print("KelanaAI")
    print("========================")
    print(f"Destination  : {destination}")
    print(f"Country      : {country}")
    print(f"Days         : {days}")
    print(f"Budget       : {budget_text} {currency}")
    print(f"Currency     : {currency}")
    print(f"Travel Month : {travel_month}")


def main() -> None:
    """Collect trip details from the terminal and display the summary."""

    destination = input("Destination  : ").strip()
    country = input("Country      : ").strip()
    days = int(input("Days         : "))
    budget = float(input("Budget       : "))
    currency = input("Currency     : ").strip()
    travel_month = input("Travel Month : ").strip()

    print()
    print_trip_summary(
        destination,
        country,
        days,
        budget,
        currency,
        travel_month,
    )


if __name__ == "__main__":
    main()
