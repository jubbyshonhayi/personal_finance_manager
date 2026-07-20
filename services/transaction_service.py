from models.transaction import Transaction
from models.financial_summary import FinancialSummary
from storage.json_storage import JsonStorage
from utils.constants import TRANSACTIONS_FILE
from utils.enums import TransactionType


class TransactionService:
    """
    Handles all business logic related to financial transactions.
    """
    
    def __init__(self, storage: JsonStorage):
        """Initializes the transaction service with a storage handler."""

        self.storage = storage


    def add_transaction(self, transaction: Transaction):
        """Adds a new transaction to storage."""

        transactions = self.storage.load_data(TRANSACTIONS_FILE)

        transactions.append(transaction.to_dict())

        self.storage.save_data(TRANSACTIONS_FILE, transactions) 


    def get_all_transactions(self):
        """Retrieves all transactions from storage."""
        
        transactions_data = self.storage.load_data(TRANSACTIONS_FILE)
        
        transactions = []
        
        for transaction_data in transactions_data:
            transactions.append(Transaction.from_dict(transaction_data))
            
        return transactions
    

    def update_transaction(self, transaction_id: str, updated_transaction: Transaction):
        """Update an existing transaction."""

        transactions = self.storage.load_data(TRANSACTIONS_FILE)

        for index, transaction in enumerate(transactions):
            if transaction["id"] == transaction_id:
                transactions[index] = updated_transaction.to_dict()
                self.storage.save_data(TRANSACTIONS_FILE, transactions)
                return
            
        raise ValueError(f"Transaction with id '{transaction_id}' not found.")
    

    def delete_transaction(self, transaction_id: str):
        """Deletes a transaction from storage."""

        transactions = self.storage.load_data(TRANSACTIONS_FILE)

        for index, transaction in enumerate(transactions):
            if transaction["id"] == transaction_id:
               transactions.pop(index)
               self.storage.save_data(TRANSACTIONS_FILE, transactions)
               return
        
        raise ValueError(f"Transaction with id '{transaction_id}' not found.")
    

    def get_financial_summary(self, user_id: str) -> FinancialSummary:
        """Calculates and returns the financial summary for the specified user."""

        transactions = self.get_all_transactions()

        total_income = 0
        total_expense = 0
        
        for transaction in transactions:

            if transaction.user_id != user_id:
                continue

            if transaction.transaction_type == TransactionType.INCOME:
                total_income += transaction.amount

            else:
                total_expense += transaction.amount

        return FinancialSummary(
            total_income=total_income,
            total_expense=total_expense,
        )

    

    
    
    

        
