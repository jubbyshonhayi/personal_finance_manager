from storage.json_storage import JsonStorage
from services.transaction_service import TransactionService
from menus.transaction_menu import (
    add_transaction_menu,
    view_transactions_menu, 
    update_transaction_menu,
    delete_transaction_menu,
    financial_summary_menu,
    financial_report_menu,                        
) 

storage = JsonStorage()

transaction_service = TransactionService(storage)

CURRENT_USER_ID = "demo-user"

def display_menu():
    """Displays the main menu."""

    print("\n===== Personal Finance Manager =====")
    print("1. Add Transaction")
    print("2. View Transactions")
    print("3. Update Transaction")
    print("4. Delete transaction")
    print("5. View Financial Summary")
    print("6. View Financial Reports")
    print("7. Exit")


def main():
    """Runs the Personal Finance Manager application."""

    while True:

        try:
            display_menu()

            choice = input("\nChoose an option: ").strip()

            if choice == "1":
                add_transaction_menu(transaction_service, CURRENT_USER_ID)
            
        
            elif choice == "2":
                view_transactions_menu(transaction_service, CURRENT_USER_ID)

            elif choice == "3":
                update_transaction_menu(transaction_service, CURRENT_USER_ID)

            elif choice == "4":
                delete_transaction_menu(transaction_service, CURRENT_USER_ID)

            elif choice == "5":
                financial_summary_menu(transaction_service, CURRENT_USER_ID)

            elif choice == "6":
                financial_report_menu(transaction_service, CURRENT_USER_ID)


            elif choice == "7":
                print("\nThank you for using Personal Finance Manager!")
                break

            else:
                print("\nInvalid option. Please try again.")

        except KeyboardInterrupt:
            print("\nProgramm interrupted. Exiting...\n")
            break


if __name__ == "__main__":
    main()