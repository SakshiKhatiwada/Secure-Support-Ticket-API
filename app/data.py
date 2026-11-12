from enum import Enum

class Role(str, Enum):
    USER = "user"
    STAFF = "staff"
    ADMIN = "admin"
    
class TicketStatus(str, Enum):
    OPEN="open"
    IN_PROGRESS="in_progress"
    RESOLVED="resolved"