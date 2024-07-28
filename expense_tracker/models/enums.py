import enum


class IntervalType(enum.Enum):
    ONCE = "ONCE"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    BI_WEEKLY = "BI_WEEKLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    SEMI_ANNUALLY = "SEMI_ANNUALLY"
    ANNUALLY = "YEARLY"


class TransactionType(enum.Enum):
    EXPENSE = "EXPENSE"
    INCOME = "INCOME"
    TRANSFER = "TRANSFER"
