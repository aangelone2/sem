"""Database mapped class.

Classes
-----------------------
Base
    Inherits DeclarativeBase, base class for mapped objects.
Expense
    Class modeling database entry.
"""


from datetime import date

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    """Inherits DeclarativeBase, base class for mapped objects."""


class Expense(Base):
    """Expense class.

    Attributes
    -----------------------
    id : int
        ID of the expense, primary key field
    date : date
        Date of the expense
    type : str
        Char representing the expense type
    amount : float
        Amount of the expense
    justification : str
        Justification for the expense
    """

    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date]
    # FIXME impose length 1
    type: Mapped[str]
    amount: Mapped[float]
    justification: Mapped[str]

    def __repr__(self) -> str:
        """Dunder representation method."""
        return (
            f"expense("
            f"id={self.id!r}, "
            f"date={self.date!r}, "
            f"type={self.type!r}, "
            f"amount={self.amount!r}, "
            f"justification={self.justification!r}"
            f")"
        )
