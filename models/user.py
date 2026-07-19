from dataclasses import dataclass
from datetime import datetime

@dataclass
class User:
    """
    Represents a registered user of the Personal Finance Manager.
    
    This model stores the user's profile information and preferences.
    """
    id: str
    name: str
    email: str
    password: str
    currency: str
    date_joined: datetime

    def to_dict(self):
        """Converts a User object into a dictionary."""
        pass
    
    @classmethod
    def from_dict(cls, data):
        """Creates a User object from a dictionary."""
        pass
    

