from storage.json_storage import JsonStorage
from services.transaction_service import TransactionService
from menus.transaction_menu import (
    add_transaction_menu,
    view_transactions_menu, 
    update_transaction_menu,
    delete_transaction_menu,
    financial_summary_menu,
    financial_report_menu,
    search_transactions_menu,  
    filter_transactions_menu                    
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
    print("4. Delete Transaction")
    print("5. Search Transactions")
    print("6. Filter Transactions")
    print("7. View Financial Summary")
    print("8. View Financial Reports")
    print("0. Exit")


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
                search_transactions_menu(transaction_service, CURRENT_USER_ID)

            elif choice == "6":
                filter_transactions_menu(transaction_service, CURRENT_USER_ID)

            elif choice == "7":
                financial_summary_menu(transaction_service, CURRENT_USER_ID)

            elif choice == "8":
                financial_report_menu(transaction_service, CURRENT_USER_ID)


            elif choice == "0":
                print("\nThank you for using Personal Finance Manager!")
                break

            else:
                print("\nInvalid option. Please try again.")
            
        except KeyboardInterrupt:
            print("\nProgramm interrupted. Exiting...\n")
            break

     
if __name__ == "__main__":
    main()