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
    

