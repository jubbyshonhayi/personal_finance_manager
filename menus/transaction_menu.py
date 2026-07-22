from datetime import datetime
import uuid

from menus.menu_helpers import(
    display_transaction_list,
    display_transaction,
    display_transaction_options,
    pause
)
from models.transaction import Transaction
from services.transaction_service import TransactionService
from utils.enums import TransactionType
from utils.constants import SEPARATOR
from utils.validators import(
    get_valid_year,
    get_valid_month,
)


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

    user_transactions = transaction_service.get_user_transactions(current_user_id)

    display_transaction_list(user_transactions, title="All Transactions")
    

def update_transaction_menu(transaction_service: TransactionService, current_user_id: str):
    """Updates an existing transaction."""

    user_transactions = transaction_service.get_user_transactions(current_user_id)

    if not user_transactions:
        print("\nNo transactions found.")
        return

    display_transaction_options(user_transactions, title="Select Transaction to Update")

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

    display_transaction(selected_transaction, title="Selected Transaction")
    
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

    user_transactions = transaction_service.get_user_transactions(current_user_id)

    if not user_transactions:
        print("\nNo transactions found.")
        return

    display_transaction_options(user_transactions, title="Select Transaction to Delete")
    
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

    display_transaction(selected_transaction, title="Selected Transaction")

    while True:

        confirmation = input("\nAre you sure you want to delete this transaction(Y/N)? ").strip().upper()

        if confirmation == "Y":
            transaction_service.delete_transaction(selected_transaction.id)
            print("\nTransaction deleted successfully!")
            return

        elif confirmation == "N":
            print("\nDeletion cancelled.")
            return

        else:
            print("Invalid choice. Try again.")
            continue


def financial_summary_menu(transaction_service: TransactionService, current_user_id: str):
    """Displays the financial summary for the current user."""

    summary = transaction_service.get_financial_summary(current_user_id)

    print("\n====== Financial Summary =====\n")

    print(f"Transactions:     {summary.transaction_count}")
    print(f"Total Income:     ${summary.total_income:.2f}")
    print(f"Total Expense:    ${summary.total_expense:.2f}")
    
    print(SEPARATOR)

    if summary.transaction_count == 0:
        status = "No Transactions"
        
    elif summary.balance > 0:
        status = "Surplus"

    elif summary.balance < 0:
        status = "Overspending"

    else:
        status = "Break Even"

    print(f"Balance:          ${summary.balance:.2f} ({status})")


    
def financial_report_menu(transaction_service: TransactionService, current_user_id: str):
    """Displays a financial report for the selected period."""

    while True:
        print("\n====== Financial Reports =====")
        print("1. Monthly Report")
        print("2. Yearly Report")

        choice = input("\nChoose report: ")

        if choice == "1":
            
            year = get_valid_year("Enter year: ")

            month = get_valid_month("Enter Month(1-12): ")

            report = transaction_service.get_financial_report(
                current_user_id,
                year,
                month
            )

            report_title = report.period.strftime("%B %Y")

            break

        elif choice == "2":
            
            year = get_valid_year("Enter Year: ")

            report = transaction_service.get_financial_report(current_user_id, year)

            report_title = report.period.strftime("%Y")

            break
            
        else:
            print("Please choose a valid option.")


    print(f"\n===== {report_title} Financial Report ======\n")

    print(f"Transactions:      {report.transaction_count}")
    print(f"Total Income:      ${report.total_income:.2f}")
    print(f"Total Expense:     ${report.total_expense:.2f}")

    print(SEPARATOR)
        
    if report.transaction_count == 0:
        status = "No Transactions"
        
    elif report.balance > 0:
        status = "Surplus"

    elif report.balance < 0:
        status = "Overspending"

    else:
        status = "Break Even"

    print(f"Balance:           ${report.balance:.2f} ({status})")

    
def search_transactions_menu(transaction_service: TransactionService, current_user_id: str):
    """Searches transactions using different criteria."""

    while True:
        print("\n====== Search Transactions ======")
        print("1. Category")
        print("2. Description")
        print("3. Transaction Type")
        print("4. Year")
        print("5. Month")
        print("6. Back")

        choice = input("\nChoose search option: ")

        if choice == "1":
            field = "category"
            value = input("Enter category: ")

        elif choice == "2":
            field = "description"
            value = input("Enter description: ")

        elif choice == "3":
            field = "transaction_type"
            value = input("Enter transaction type (Income/Expense): ")

        elif choice == "4":
            field = "year"
            value = get_valid_year("Enter year: ")

        elif choice == "5":
            field = "month"
            value = get_valid_month("Enter month (1-12): ")

        elif choice == "6":
            return

        else:
            print("Please choose a valid option.")
            continue

        results = transaction_service.search_transactions(current_user_id, field, value)

        display_transaction_list(
            results,
            title="Search Results",
            empty_message="No matching transactions found."
        )
        

def filter_transactions_menu(transaction_service: TransactionService, current_user_id: str):
    """Filters transactions based on user-selected criteria."""

    while True:
        print("\n====== Filter Transactions ======")
        print("1. Income Transactions")
        print("2. Expense Transactions")
        print("3. Date Range")
        print("4. Amount Range")
        print("5. Back")

        choice = input("\nChoose filter: ").strip()

        if choice == "1":
            results = transaction_service.filter_transactions(
                current_user_id,
                "transaction_type",
                TransactionType.INCOME,
            )

            display_transaction_list(
                results,
                title="Income Transactions",
            )
            

        elif choice == "2":
            results = transaction_service.filter_transactions(
                current_user_id,
                "transaction_type",
                TransactionType.EXPENSE,
            )

            display_transaction_list(
                results,
                title="Expense Transactions",
            )
            

        elif choice == "3":

            while True:

                try:
                    start_date = datetime.strptime(
                        input("Start date (YYYY-MM-DD): ").strip(),
                        "%Y-%m-%d"
                    )

                    end_date = datetime.strptime(
                        input("End date (YYYY-MM-DD): ").strip(),
                        "%Y-%m-%d"
                    )

                    if start_date > end_date:
                        print("Start date cannot be after end date.")
                        continue

                    break

                except ValueError:
                    print("Please enter dates in YYYY-MM-DD format.")

            results = transaction_service.filter_transactions(
                current_user_id,
                "date_range",
                (start_date, end_date),
            )

            display_transaction_list(
                results,
                title=f"Transactions ({start_date:%Y-%m-%d} to {end_date:%Y-%m-%d})",
            )
   
        elif choice == "4":

            while True:
                try:
                    minimum_amount = float(input("Minimum amount: "))
                    maximum_amount = float(input("Maximum amount: "))

                    if minimum_amount < 0 or maximum_amount < 0:
                        print("Amounts cannot be negative.")
                        continue

                    if minimum_amount > maximum_amount:
                        print("Minimum amount cannot be greater than maximum amount.")
                        continue

                    break

                except ValueError:
                    print("Please enter valid amounts.")

            results = transaction_service.filter_transactions(
                current_user_id,
                "amount_range",
                (minimum_amount, maximum_amount),
            )

            display_transaction_list(
                results,
                title=f"Transactions (${minimum_amount:.2f} - ${maximum_amount:.2f})",
            )
            

        elif choice == "5":
            return

        else:
            print("Please choose a valid option.")