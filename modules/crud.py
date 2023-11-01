"""Class mediating CRUD operations on the DB.

Class
-----------------------
CRUDHandler
    Class mediating CRUD operations.
"""

# Copyright (c) 2023 Adriano Angelone
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the
# Software.
#
# This file is part of sem-cli.
#
# This file may be used under the terms of the GNU General
# Public License version 3.0 as published by the Free Software
# Foundation and appearing in the file LICENSE included in the
# packaging of this file.  Please review the following
# information to ensure the GNU General Public License version
# 3.0 requirements will be met:
# http://www.gnu.org/copyleft/gpl.html.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


from datetime import date
import csv

from typing import List
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy import func
from sqlalchemy.orm import Session

from modules.common import str2date
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

    add()
        Add expense to the DB.
    query()
        Return expenses within time period.
    summarize()
        Return summary of expenses grouped by type within period.
    load()
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
        data : ExpenseAdd
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
        start: Optional[date] = None,
        end: Optional[date] = None,
        types: Optional[List[str]] = None,
    ) -> List[ExpenseRead]:
        """Return expenses in time window.

        Parameters
        -----------------------
        start, end : Optional[date], default=None
            Starting and ending dates, any date if either is None
        types : Optional[List[str]], default=None
            Types to be selected in the result, all if None

        Returns
        -----------------------
        List[ExpenseRead]
            List of expenses matching the criteria
        """

        if (start is None) or (end is None):
            date_condition = True
        else:
            date_condition = Expense.date.between(start, end)

        if types is None:
            type_condition = True
        else:
            type_condition = Expense.type.in_(types)

        return self.db.scalars(
            select(Expense)
            .where(date_condition)
            .where(type_condition)
            .order_by(Expense.date)
        ).all()

    def summarize(
        self,
        start: Optional[date] = None,
        end: Optional[date] = None,
        types: Optional[List[str]] = None,
    ):
        """Return summary of expenses grouped by type within period.

        Parameters
        -----------------------
        start, end : date | None, default=None
            Starting and ending dates, any date if either is None
        types : Optional[List[str]], default=None
            Types to be selected in the result, all if None

        Returns
        -----------------------
        List[Tuple[str, float]]
            List of Tuples, each containing expense type and summed amounts
        """
        if (start is None) or (end is None):
            date_condition = True
        else:
            date_condition = Expense.date.between(start, end)

        if types is None:
            type_condition = True
        else:
            type_condition = Expense.type.in_(types)

        return self.db.execute(
            select(Expense.type, func.sum(Expense.amount))
            .where(date_condition)
            .where(type_condition)
            .group_by(Expense.type)
            .order_by(Expense.type)
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
                    date=str2date(row[1]),
                    type=row[2],
                    amount=row[3],
                    justification=row[4],
                )

                self.db.add(record)

            # Committing only at the end for speed
            self.db.commit()
