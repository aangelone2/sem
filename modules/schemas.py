"""Types for CRUD operations.

Classes
-----------------------
expense_base
    Base expense class.
"""


from datetime import datetime
from pydantic import BaseModel


class expense_base(BaseModel):
    """Base expense class.

    Attributes
    -----------------------
    date : datetime
        Date of the expense
    type : str
        Char representing the type of the expense
    amount : float
        Amount (positive or negative) of the expense
    justification : str
        Justification for the expense
    """

    date: datetime
    # FIXME impose length 1
    type: str
    amount: float
    justification: str

    class Config:
        """Required for SQLAlchemy models."""

        orm_mode = True


class expense_add(expense_base):
    """Derived expense class for insertion operations."""


class expense_query(expense_base):
    """Derived expense class for query operations.

    Attributes
    -----------------------
    id : int
        Expense ID (primary key)
    """

    id: int
