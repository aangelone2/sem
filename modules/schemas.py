"""Types for CRUD operations.

Classes
-----------------------
ExpenseBase
    Base expense class.
ExpenseAdd
    Derived expense class for insertion operations.
class ExpenseRead
    Derived expense class for query operations.
"""


from datetime import datetime
from pydantic import BaseModel


class ExpenseBase(BaseModel):
    """Base expense class.

    Attributes
    -----------------------
    date : datetime
        Date of the expense
    type : str
        Char representing the expense type
    amount : float
        Amount of the expense
    justification : str
        Justification for the expense
    """

    date: datetime
    # FIXME impose length 1
    type: str
    amount: float
    justification: str


class ExpenseAdd(ExpenseBase):
    """Expense for insertion operations."""


class ExpenseRead(ExpenseBase):
    """Expense for selection operations.

    Attributes
    -----------------------
    id : int
        Expense ID (primary key)
    """

    id: int
