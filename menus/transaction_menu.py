from datetime import datetime
import uuid

from models.transaction import Transaction
from services.transaction_service import TransactionService
from utils.enums import TransactionType
from utils.constants import SEPARATOR


def add_transaction_menu(transaction_service: TransactionService, current_user_id: str):
    """Collects transaction details from the user and adds a new transaction."""
        
    print("\n=== Add Transaction ===")
        
    while True:
        try:
                
            amount = float(input("Amount: "))
                
            if amount <= 0:
                print("Amount must be greater than zero.")
                continue
                
            break

        except ValueError:
            print("Please enter a valid amount.")
                
            
    while True:
        print("\nTransaction Type")
        print("1. Income")
        print("2. Expense")
                
        transaction_type_choice = input("Choose transaction type: ").strip()
                
        if transaction_type_choice == "1":
            transaction_type = TransactionType.INCOME
            break

        elif transaction_type_choice == "2":
            transaction_type = TransactionType.EXPENSE
            break
                
        else:
            print("Invalid option. Please try again.")


    while True:
        category = input("\nCategory: ").strip()
        if category:
            break
        
        print("Category cannot be empty.")

    while True:
        description = input("Description: ").strip()
        if description:
            break
        
        print("Description cannot be empty.")

    transaction = Transaction(
        id=str(uuid.uuid4()),
        user_id=current_user_id,
        amount=amount,
        transaction_type=transaction_type,
        category=category,
        description=description,
        date=datetime.now(),
    )

    transaction_service.add_transaction(transaction)

    print("\nTransaction added successfully!")


def view_transactions_menu(transaction_service: TransactionService, current_user_id: str):
    """Displays all transactions belonging to the current user."""

    transactions = transaction_service.get_all_transactions()

    user_transactions = []

    for transaction in transactions:
        if transaction.user_id == current_user_id:
            user_transactions.append(transaction)
    
    if not user_transactions:
        print("\nNo transactions found.")
        return
    
    print("\n===== Your Transactions =====\n")
    print(f"Total Transactions: {len(user_transactions)}")
    
    for index, transaction in enumerate(user_transactions, start=1):
        print(f"\n{SEPARATOR}")
        print(f"\nTransaction #{index}")
        print(f"Type:                   {transaction.transaction_type.value}")
        print(f"Amount:                 ${transaction.amount:.2f}")
        print(f"Category:               {transaction.category.title()}")
        print(f"Description:            {transaction.description.capitalize()}")
        print(f"Date:                   {transaction.date.strftime('%Y-%m-%d %H:%M')}")


def update_transaction_menu(transaction_service: TransactionService, current_user_id: str):
    """Updates an existing transaction."""

    transactions = transaction_service.get_all_transactions()

    user_transactions = []

    for transaction in transactions:
        if transaction.user_id == current_user_id:
            user_transactions.append(transaction)

    if not user_transactions:
        print("\nNo transactions found.")
        return

    print("\n===== Select Transaction to Update =====")

    for index, transaction in enumerate(user_transactions, start=1):
        print(f"{index}. " f"{transaction.category.title()}   -  " f"${transaction.amount:.2f}")

    while True:
        try:
            choice = int(input("\nSelect transaction: "))

            if choice < 1 or choice > len(user_transactions):
                print("Invalid transaction selection.")
                continue

            break

        except ValueError:
            print("Please enter a valid number.")

    selected_transaction = user_transactions[choice - 1]

    print("\n===== Current Transaction =====")
    print(f"Type:                {selected_transaction.transaction_type.value}")
    print(f"Amount:              ${selected_transaction.amount:.2f}")
    print(f"Category:            {selected_transaction.category.title()}")
    print(f"Description:         {selected_transaction.description.capitalize()}")
    print(f"Date:                {selected_transaction.date.strftime('%Y-%m-%d %H:%M')}")

    while True:
        print("\n===== Update Options =====")
        print("1. Amount")
        print("2. Transaction Type")
        print("3. Category")
        print("4. Description")
        print("5. Cancel")

        option = input("\nChoose what to update: ").strip()

        if option == "1":
            while True:
                try:
                    amount = float(input("New amount: "))

                    if amount <= 0:
                        print("Amount must be greater than zero.")
                        continue

                    selected_transaction.amount = amount
                    break

                except ValueError:
                    print("Please enter a valid amount.")

        elif option == "2":
            while True:
                print("\nTransaction Type")
                print("1. Income")
                print("2. Expense")

                transaction_type_choice = input("Choose transaction type: ").strip()

                if transaction_type_choice == "1":
                    selected_transaction.transaction_type = TransactionType.INCOME
                    break

                elif transaction_type_choice == "2":
                    selected_transaction.transaction_type = TransactionType.EXPENSE
                    break

                else:
                    print("Invalid option.")

        elif option == "3":
            while True:
                category = input("New category: ").strip()

                if category:
                    selected_transaction.category = category
                    break

                print("Category cannot be empty.")

        elif option == "4":
            while True:
                description = input("New description: ").strip()

                if description:
                    selected_transaction.description = description
                    break

                print("Description cannot be empty.")

        elif option == "5":
            print("\nUpdate cancelled.")
            return

        else:
            print("Invalid option.")
            continue

        transaction_service.update_transaction(
            selected_transaction.id,
            selected_transaction
        )

        print("\nTransaction updated successfully!")
        return
     

def delete_transaction_menu(transaction_service: TransactionService, current_user_id: str):
    """Deletes a selected transaction."""

    transactions = transaction_service.get_all_transactions()

    user_transactions = []

    for transaction in transactions:
        if transaction.user_id == current_user_id:
            user_transactions.append(transaction)

    if not user_transactions:
        print("\nNo transactions found.")
        return

    print("\n===== Select Transaction to Delete =====")

    for index, transaction in enumerate(user_transactions, start=1):
        print(f"{index}. " f"{transaction.category.title()}   -  " f"${transaction.amount:.2f}")
    
    while True:
        try:
            choice = int(input("\nSelect transaction: "))

            if choice < 1 or choice > len(user_transactions):
                print("Invalid transaction selection.")
                continue

            break

        except ValueError:
            print("Please enter a valid number.")

    selected_transaction = user_transactions[choice - 1]

    print("\n===== Selected Transaction =====")
    print(f"Type:                {selected_transaction.transaction_type.value}")
    print(f"Amount:              ${selected_transaction.amount:.2f}")
    print(f"Category:            {selected_transaction.category.title()}")
    print(f"Description:         {selected_transaction.description.capitalize()}")
    print(f"Date:                {selected_transaction.date.strftime('%Y-%m-%d %H:%M')}")
    
    while True:

        choice = input("\nAre you sure you want to delete this transaction(Y/N)? ").strip().upper()

        if choice == "Y":
            transaction_service.delete_transaction(selected_transaction.id)
            print("\nTransaction deleted successfully!")
            return

        elif choice == "N":
            print("Deletion cancelled.")
            return

        else:
            print("Invalid choice. Try again.")
            continue


def financial_summary_menu(transaction_service: TransactionService, current_user_id: str):
    """Displays the financial summary for the current user."""

    summary = transaction_service.get_financial_summary(current_user_id)

    print("\n====== Financial Summary =====\n")

    print(f"Total Income:     ${summary.total_income:.2f}")
    print(f"Total Expense:    ${summary.total_expense:.2f}")
    
    print("-"*50)

    if summary.balance > 0:
        print(f"Balance:          ${summary.balance:.2f} (Surplus)")
    
    elif summary.balance < 0:
        print(f"Balance:          ${summary.balance:.2f} (Overspending)")

    else:
        print(f"Balance:          ${summary.balance:.2f} (Break Even)")

