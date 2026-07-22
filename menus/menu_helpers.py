from models.transaction import Transaction
from utils.constants import SEPARATOR


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

    for transaction in transactions:
        print(f"Date:          {transaction.date.strftime('%d %b %Y')}")
        print(f"Type:          {transaction.transaction_type.value}")
        print(f"Category:      {transaction.category}")
        print(f"Amount:        ${transaction.amount:.2f}")
        print(f"Description:   {transaction.description}")

        print(SEPARATOR)