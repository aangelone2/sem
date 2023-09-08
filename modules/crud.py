"""Functions for CRUD operations on the database.

Functions
-----------------------
query()
    Search for Incidents with closest match to Alarm list.
"""


from datetime import datetime

from typing import List
from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.models import expense


def query(
    db: Session,
    start: datetime | None = None,
    end: datetime | None = None,
) -> List[expense]:
    """Search for expenses within time period.

    Parameters
    -----------------------
    db : Session
        Connection to the database
    start, end : datetime | None, default=None
        Starting and ending dates, ignored if either is None

    Returns
    -----------------------
    List[expense]
        List of expenses matching the criteria, all expenses if
        either of the dates is None
    """
    if (start is None) or (end is None):
        return db.scalars(
            select(expense).order_by(expense.date)
        )

    return db.scalars(
        select(expense)
        .where(expense.date.between(start, end))
        .order_by(expense.date)
    )
