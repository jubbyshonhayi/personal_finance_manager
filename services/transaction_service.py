from datetime import datetime
from models.transaction import Transaction
from models.financial_summary import FinancialSummary, FinancialReport
import pandas as pd
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


    def get_user_transactions(self, user_id: str) -> list[Transaction]:
        """
        Returns all transactions belonging to the specified user.
        """

        transactions = self.get_all_transactions()

        user_transactions = []

        for transaction in transactions:
            if transaction.user_id == user_id:
                user_transactions.append(transaction)

        return user_transactions
    

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
        transaction_count = 0
        
        for transaction in transactions:

            if transaction.user_id != user_id:
                continue

            transaction_count += 1

            if transaction.transaction_type == TransactionType.INCOME:
                total_income += transaction.amount

            else:
                total_expense += transaction.amount

        return FinancialSummary(
            total_income=total_income,
            total_expense=total_expense,
            transaction_count=transaction_count,
        )
    
    
    def get_financial_report(self, user_id: str, year: int, month: int | None=None) -> FinancialReport:
        """Generates a financial report for the specified period."""

        transactions = self.get_all_transactions()

        total_income = 0
        total_expense = 0
        transaction_count = 0

        for transaction in transactions:
            if transaction.user_id != user_id:
                continue

            if transaction.date.year != year:
                continue

            if month is not None and transaction.date.month != month:
                continue

            transaction_count += 1

            if transaction.transaction_type == TransactionType.INCOME:
                total_income += transaction.amount

            else:
                total_expense += transaction.amount


        if month is not None:
            period = datetime(year, month, 1)

        else:
            period = datetime(year, 1, 1)

        return FinancialReport(
            total_income=total_income,
            total_expense=total_expense,
            period=period,
            transaction_count=transaction_count,
        )

    
    def search_transactions(self, user_id: str, field: str, value) -> list[Transaction]:
        """Searches transactions using the specified field and value."""

        transactions = self.get_all_transactions()

        transactions_data  = []

        for transaction in transactions:
            transactions_data.append(transaction.to_dict())

        df = pd.DataFrame(transactions_data)

        # Keep only the current user's transactions.
        df = df[df["user_id"] == user_id]

        df["date_time"] = pd.to_datetime(df["date"])

        df["year"] = df["date_time"].dt.year
        df["month"] = df["date_time"].dt.month

        if field in ("category", "description", "transaction_type"):
            filtered_df = df[df[field].str.lower() == value.lower()]

        else:
            filtered_df = df[df[field] == value]

        filtered_df = filtered_df.drop(columns=["date_time", "year", "month"])

        filtered_transactions = []

        for transaction in filtered_df.to_dict(orient="records"):
            filtered_transactions.append(Transaction.from_dict(transaction))

        return filtered_transactions

    

        
        







    

    
    
    

        
