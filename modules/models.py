"""Database mapped class.

Classes
-----------------------
Expense
    Class modeling database entry.
"""


from datetime import datetime

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class base(DeclarativeBase):
    """Inherits DeclarativeBase, base class for mapped objects."""


class expense(base):
    """Expense class.

    Attributes
    -----------------------
    id : int
        ID of the expense, primary key field
    date : datetime
        Date of the expense
    type : str
        Char representing the type of the expense
    amount : float
        Amount (positive or negative) of the expense
    justification : str
        Justification for the expense
    """

    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime]
    # FIXME impose length 1
    type: Mapped[str]
    amount: Mapped[float]
    justification: Mapped[str]
