def get_valid_year(prompt: str) -> int:
    """
    Prompts the user for a valid positive year.

    Repeats until the user enters a valid year greater than zero.
    """

    while True:
        try:
            year = int(input(prompt))

            if year < 1000:
                print("Please enter a valid four-digit year.")
                continue

            return year

        except ValueError:
            print("Please enter a valid year.")


def get_valid_month(prompt: str) -> int:
    """
    Prompts the user for a valid month.

    Repeats until the user enters a month between 1 and 12.
    """

    while True:
        try:
            month = int(input(prompt))

            if month < 1 or month > 12:
                print("Month must be between 1 and 12.")
                continue

            return month

        except ValueError:
            print("Please enter a valid month.")

