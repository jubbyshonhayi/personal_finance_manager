from models.transaction import Transaction
from storage.json_storage import JsonStorage
from utils.constants import TRANSACTIONS_FILE


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

    
    
    

        
