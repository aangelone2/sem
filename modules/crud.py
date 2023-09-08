"""Class mediating CRUD operations on the DB.

Class
-----------------------
crud_handler
    Class mediating CRUD operations on the DB.
"""


from datetime import datetime

from typing import List
from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.models import base
from modules.models import expense
from modules.schemas import expense_add
from modules.schemas import expense_query


class crud_handler:
    """Class mediating CRUD operations on the DB.

    Attributes
    -----------------------
    db : Session
        Link to the DB

    Public methods
    -----------------------
    __init__(str, bool)
        Construct class instance.

    add(expense_add)
        Add expense to the DB.

    query(datetime | None, datetime | None) -> List[expense]
        Return expenses within time period.
    """

    def __init__(self, path: str, new: bool = True):
        """Construct class instance.

        Parameters
        -----------------------
        path : str
            Path the DB should be located in
        new : bool, default=True
            If True, DB is created (or overwritten)
        """
        self.db = None

        engine_str = "sqlite+pysqlite:///"
        self.db = Session(
            bind=create_engine(engine_str + path)
        )

        # Applying existing schema if requested
        if new:
            base.metadata.create_all(self.db.get_bind())

    def add(self, data: expense_add):
        """Add expense to the DB.

        Parameters
        -----------------------
        data : expense_add
            Expense data.
        """
        # Primary key added automatically
        new_expense = expense(
            date=data.date,
            type=data.type,
            amount=data.amount,
            justification=data.justification,
        )
        self.db.add(new_expense)
        self.db.commit()
        self.db.refresh(new_expense)

    def query(
        self,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> List[expense_query]:
        """Return expenses within time period.

        Parameters
        -----------------------
        start, end : datetime | None, default=None
            Starting and ending dates, ignored if either is None

        Returns
        -----------------------
        List[expense_query]
            List of expenses matching the criteria, all expenses if
            either of the dates is None
        """
        if (start is None) or (end is None):
            return self.db.scalars(
                select(expense).order_by(expense.date)
            ).all()

        return self.db.scalars(
            select(expense)
            .where(expense.date.between(start, end))
            .order_by(expense.date)
        ).all()
