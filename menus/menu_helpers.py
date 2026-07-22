from models.transaction import Transaction
from utils.constants import SEPARATOR

CATEGORY_WIDTH = 20
AMOUNT_WIDTH = 10

TRANSACTIONS_PER_PAGE = 10

def pause(message: str = "\nPress Enter to continue..."):
    """Pauses the program until the user presses Enter."""

    input(message)


def display_transaction_list(
    transactions: list[Transaction],
    title: str = "Transactions",
    empty_message: str = "No transactions found.",
):
    """
    Displays a formatted list of transactions.

    Args:
        transactions: The transactions to display.
        title: The heading displayed above the transaction list.
        empty_message: The message displayed when no transactions are found.
    """

    if not transactions:
        print(f"\n{empty_message}")
        return
    
     
    print(f"\n====== {title} ======\n")
    print(f"Transactions:  {len(transactions)}\n")

    for start in range(0, len(transactions), TRANSACTIONS_PER_PAGE):
        end = start + TRANSACTIONS_PER_PAGE
        page = transactions[start:end]

        for index, transaction in enumerate(page, start=start + 1):

            print(f"Transaction #{index}")
            print(f"Type:          {transaction.transaction_type.value}")
            print(f"Amount:        ${transaction.amount:.2f}")
            print(f"Category:      {transaction.category.title()}")
            print(f"Description:   {transaction.description.capitalize()}")
            print(f"Date:          {transaction.date.strftime('%d %b %Y')}")

            print(SEPARATOR)

        if end < len(transactions):
            pause("\nPress Enter for next page...")
        else:
            pause("\nEnd of results. Press Enter to continue...")


def display_transaction(
    transaction: Transaction,
    title: str = "Transaction",
):
    """
    Displays a formatted transaction.
    """

    print(f"\n===== {title} =====\n")

    print(f"ID:            {transaction.id}")
    print(f"Type:          {transaction.transaction_type.value}")
    print(f"Amount:        ${transaction.amount:.2f}")
    print(f"Category:      {transaction.category.title()}")
    print(f"Description:   {transaction.description.capitalize()}")
    print(f"Date:          {transaction.date.strftime('%Y-%m-%d %H:%M')}")

    print(SEPARATOR)


def display_transaction_options(
    transactions: list[Transaction],
    title: str = "Select Transaction",
):
    """
    Displays a numbered list of transactions for user selection.
    """

    print(f"\n===== {title} =====\n")

    for index, transaction in enumerate(transactions, start=1):
        print(
            f"{index:>2}. "
            f"{transaction.category.title():<{CATEGORY_WIDTH}}"
            f"${transaction.amount:>{AMOUNT_WIDTH}.2f}   "
            f"{transaction.date.strftime('%d %b %Y')}"
        )

    print(SEPARATOR)