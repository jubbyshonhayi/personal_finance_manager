from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass
class User:
    """
    Represents a registered user of the Personal Finance Manager.
    
    This model stores the user's profile information and preferences.
    """
    id: UUID
    username: str
    email: str
    password_hash: str
    date_joined: datetime

