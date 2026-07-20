from dataclasses import dataclass
from datetime import datetime
from utils.enums import TransactionType

@dataclass
class Transaction:
    """
    Represents a financial transaction made by a user.

    Transactions can represent either income or expenses and are used 
    to generate financial reports and insights.
    """
    id: str
    user_id: str
    amount: float
    transaction_type: TransactionType
    category: str
    description: str
    date: datetime 


    def to_dict(self) -> dict:
        """
        Converts the transaction object into a dictionary that can be
        serialized and stored as JSON.
        """

        return {
            "id": self.id,
            "user_id": self.user_id,
            "amount": self.amount,
            "transaction_type": self.transaction_type.value,
            "category": self.category,
            "description": self.description,
            "date": self.date.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Transaction":
        """Creates a Transaction object from a dictionary."""
        
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            amount=data["amount"],
            transaction_type=TransactionType(data["transaction_type"]),
            category=data["category"],
            description=data["description"],
            date=datetime.fromisoformat(data["date"]),
        )
