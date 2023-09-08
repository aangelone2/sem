"""Class mediating CRUD operations on the DB.

Class
-----------------------
CRUDHandler
    Class mediating CRUD operations.
"""


from datetime import datetime
import csv

from typing import List
from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.models import Base
from modules.models import Expense
from modules.schemas import ExpenseAdd
from modules.schemas import ExpenseRead


class CRUDHandler:
    """Class mediating CRUD operations.

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
    load(str)
        Append the contents of a CSV file to the database.
    """

    def __init__(self, path: str, new: bool = True):
        """Construct class instance.

        Parameters
        -----------------------
        path : str
            Path the DB should be located in
        new : bool, default=True
            If True, DB created/overwritten
        """
        self.db = None

        cstr = "sqlite+pysqlite:///"
        self.db = Session(bind=create_engine(cstr + path))

        # Resetting schema
        if new:
            Base.metadata.drop_all(self.db.get_bind())
            Base.metadata.create_all(self.db.get_bind())

    def add(self, data: ExpenseAdd):
        """Add expense to the DB.

        Parameters
        -----------------------
        data : expense_add
            Expense data.
        """
        # Primary key added automatically
        new_expense = Expense(
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
    ) -> List[ExpenseRead]:
        """Return expenses in time window.

        Parameters
        -----------------------
        start, end : datetime | None, default=None
            Starting and ending dates, ignored if either is None

        Returns
        -----------------------
        List[ExpenseRead]
            List of expenses matching the criteria, all expenses if
            either of the dates is None
        """
        if (start is None) or (end is None):
            return self.db.scalars(
                select(Expense).order_by(Expense.date)
            ).all()

        return self.db.scalars(
            select(Expense)
            .where(Expense.date.between(start, end))
            .order_by(Expense.date)
        ).all()

    def load(self, filename: str):
        """Append the contents of a CSV file to the database.

        Parameters
        -----------------------
        filename : str
            Filename of the input CSV file
        """
        with open(
            filename, "r", newline="", encoding="utf-8"
        ) as csvfile:
            reader = csv.reader(csvfile, quotechar='"')

            for row in reader:
                record = Expense(
                    id=row[0],
                    date=datetime.strptime(row[1], "%Y-%m-%d"),
                    type=row[2],
                    amount=row[3],
                    justification=row[4],
                )

                self.db.add(record)

            # Committing only at the end for speed
            self.db.commit()
