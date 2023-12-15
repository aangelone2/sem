"""Class mediating CRUD operations on the DB.

Classes
-----------------------
CRUDHandlerError
    Exception raised for errors in DB operations.
CRUDHandler
    Class mediating CRUD operations.

Functions
-----------------------
str2date()
    Convert string in YYYY-MM-DD format to date.
"""

# Copyright (c) 2023 Adriano Angelone
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# This file is part of sem.
#
# This file may be used under the terms of the GNU General Public License
# version 3.0 as published by the Free Software Foundation and appearing in the
# file LICENSE included in the packaging of this file. Please review the
# following information to ensure the GNU General Public License version 3.0
# requirements will be met:
# http://www.gnu.org/copyleft/gpl.html.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import os
from datetime import datetime
import csv

from pydantic import ValidationError

from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy import func
from sqlalchemy import and_
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from sqlalchemy_utils import database_exists
from sqlalchemy_utils import create_database

from modules.models import Base
from modules.models import Expense
from modules.schemas import ExpenseAdd
from modules.schemas import ExpenseUpdate
from modules.schemas import QueryParameters


def str2date(arg: str) -> datetime.date:
    """Convert string in YYYY-MM-DD format to date.

    Parameters
    -----------------------
    arg : str
        The string to convert.

    Returns
    -----------------------
    datetime.date
        The converted date.
    """
    return datetime.strptime(arg, "%Y-%m-%d").date()


class CRUDHandlerError(Exception):
    """Exception raised for errors in DB operations."""


class CRUDHandler:
    """Class mediating CRUD operations.

    Attributes
    -----------------------
    db : Session
        Link to the DB.

    Public methods
    -----------------------
    __init__()
        Construct class instance.
    close()
        Close DB connection.
    add()
        Add expense to the DB.
    query()
        Return expenses matching specified filters.
    summarize()
        Summarize expenses matching specified filters.
    update()
        Update expense selected by ID.
    remove()
        Remove selected expenses from the DB.
    erase()
        Remove all expenses from the DB.
    load()
        Append the contents of a CSV file to the database.
    save()
        Save the current contents of the DB to a CSV file.
    """

    def __init__(self):
        """Construct class instance."""
        DRIVER = "postgresql+psycopg"
        USER = "postgres"
        PASSWORD = ""
        HOST = "localhost"
        PORT = "5432"
        DATABASE = "sem-test" if os.environ.get("SEM_TEST") == "1" else "sem"

        DB = f"{DRIVER}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
        if not database_exists(DB):
            create_database(DB)

        engine = create_engine(DB)
        # Building schema
        Base.metadata.create_all(engine)

        self.db = Session(bind=engine)

    def close(self):
        """Close DB connection."""
        self.db.close()

    def add(self, data: ExpenseAdd):
        """Add expense to the DB.

        Parameters
        -----------------------
        data : ExpenseAdd
            Expense data.
        """
        # Primary key added automatically
        self.db.add(Expense(**data.model_dump()))
        self.db.commit()

    def _build_query_conditions(self, params: QueryParameters):
        if params.start is None:
            start_condition = True
        else:
            start_condition = Expense.date >= params.start

        if params.end is None:
            end_condition = True
        else:
            end_condition = Expense.date <= params.end

        if params.types is None:
            type_condition = True
        else:
            type_condition = Expense.type.in_(params.types)

        if params.categories is None:
            cat_condition = True
        else:
            cat_condition = Expense.category.in_(params.categories)

        return and_(
            start_condition, end_condition, type_condition, cat_condition
        )

    def query(self, params: QueryParameters) -> list[Expense]:
        """Return expenses matching specified filters.

        Parameters
        -----------------------
        params : QueryParameters
            Parameters of the query.

        Returns
        -----------------------
        list[Expense]
            List of expenses matching the criteria.
        """
        return self.db.scalars(
            select(Expense)
            .where(self._build_query_conditions(params))
            .order_by(Expense.date)
        ).all()

    def summarize(
        self, params: QueryParameters
    ) -> dict[str, dict[str, float]]:
        """Summarize expenses matching specified filters.

        Parameters
        -----------------------
        params : QueryParameters
            Parameters of the query.

        Returns
        -----------------------
        dict[dict[str, float]]
            Dictionary containing inner {type: amount} dictionaries,
            grouped by category.
        """
        sums = self.db.execute(
            select(
                Expense.category,
                Expense.type,
                (func.sum(Expense.amount)).label("sum"),
            )
            .where(self._build_query_conditions(params))
            .group_by(Expense.category, Expense.type)
            .order_by(Expense.category, Expense.type)
        ).all()

        res = {}

        # Creating outer dictionaries
        for s in sums:
            res[s.category] = {}

        # Creating inner dictionaries
        for s in sums:
            res[s.category][s.type] = s.sum

        return res

    def update(self, ID: int, data: ExpenseUpdate):
        """Update expense selected by ID.

        Parameters
        -----------------------
        ID : int
            ID of the expense to update.
        data : ExpenseUpdate
            New data to patch the expense with. Unset fields will not change.

        Raises
        -----------------------
        CRUDHandlerError
            If specified ID is not found.
        """
        exp = self.db.get(Expense, ID)
        if exp is None:
            raise CRUDHandlerError(f"ID {ID} not found")

        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(exp, k, v)
        self.db.commit()

    def remove(self, ids: list[int]):
        """Remove selected expenses from the DB.

        Parameters
        -----------------------
        ids : list[int]
            IDs of the removed expenses.

        Raises
        -----------------------
        CRUDHandlerError
            If a specified ID is not found.
        """
        for ID in ids:
            exp = self.db.get(Expense, ID)
            if exp is None:
                self.db.rollback()
                raise CRUDHandlerError(f"ID {ID} not found")

            self.db.delete(exp)

        self.db.commit()

    def erase(self):
        """Remove all expenses from the DB."""
        for exp in self.query(QueryParameters()):
            self.db.delete(exp)

        # Resetting primary key
        self.db.execute(text("ALTER SEQUENCE expenses_id_seq RESTART"))
        self.db.commit()

    def load(self, filename: str):
        """Append the contents of a CSV file to the database.

        The file should not contain headers, and have fields ordered as
        date -> type -> category -> amount -> description.

        Parameters
        -----------------------
        filename : str
            Filename of the input CSV file.

        Raises
        -----------------------
        FileNotFoundError
            - If file not found.
        CRUDHandlerError
            - If line with invalid number of fields is found.
            - If line with invalid field is found.
        """
        NUM_FIELDS = 5

        try:
            with open(filename, "r", newline="", encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile, quotechar='"')

                for ir, row in enumerate(reader):
                    if len(row) != NUM_FIELDS:
                        raise CRUDHandlerError(
                            f"{filename} :: {ir+1} :: invalid field number"
                        )

                    try:
                        exp = ExpenseAdd(
                            date=str2date(row[0]),
                            type=row[1],
                            category=row[2],
                            amount=row[3],
                            description=row[4],
                        )
                    except ValidationError as err:
                        raise CRUDHandlerError(
                            f"{filename} :: {ir+1} :: invalid field"
                        ) from err

                    self.db.add(Expense(**exp.model_dump()))
        except FileNotFoundError as err:
            raise FileNotFoundError(f"{filename} not found") from err
        except CRUDHandlerError:
            self.db.rollback()
            raise

        self.db.commit()

    def save(self, filename: str):
        """Save the current contents of the DB to a CSV file.

        The file will not contain headers, and fields will be ordered as
        date -> type -> category -> amount -> description.

        Parameters
        -----------------------
        filename : str
            Filename of the output CSV file.
        """
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(
                csvfile, quotechar='"', quoting=csv.QUOTE_NONNUMERIC
            )

            expenses = self.query(QueryParameters())

            for ex in expenses:
                writer.writerow(
                    [ex.date, ex.type, ex.category, ex.amount, ex.description]
                )
