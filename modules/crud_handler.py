"""Class mediating CRUD operations on the DB.

Classes
-----------------------
CRUDHandler

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
from datetime import date
from datetime import datetime
import csv
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field
from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from sqlalchemy_utils import database_exists
from sqlalchemy_utils import create_database

from modules.models import Base
from modules.models import Expense
from modules.schemas import ExpenseAdd
from modules.schemas import ExpenseRead


def str2date(arg: str) -> datetime.date:
    """Convert string in YYYY-MM-DD format to date.

    Parameters
    -----------------------
    arg : str
        The string to convert

    Returns
    -----------------------
    datetime.date
        The converted datetime
    """
    return datetime.strptime(arg, "%Y-%m-%d").date()


class QueryParameters(BaseModel):
    """Strong type for query parameters.

    Attributes
    -----------------------
    start : Optional[date]
        Query start date. If `None`, dates will not be used. Default is `None`.
    end : Optional[date]
        Query end date. If `None`, dates will not be used. Default is `None`.
    types : Optional[List[str]]
        Types to filter the query. If `None`, all types. Default is `None`.
    categories : Optional[List[str]]
        Categories to filter the query. If `None`, all types. Default is
        `None`.
    """

    start: Optional[date] = Field(
        default=None,
        description="""Query start date. If `None`, dates will not be used.
        Default is `None`.""",
    )
    end: Optional[date] = Field(
        default=None,
        description="""Query end date. If `None`, dates will not be used.
        Default is `None`.""",
    )
    types: Optional[List[str]] = Field(
        default=None,
        description="""Types to filter the query. If `None`, all types. Default
        is `None`.""",
    )
    categories: Optional[List[str]] = Field(
        default=None,
        description="""Categories to filter the query. If `None`, all types.
        Default is `None`.""",
    )


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
        Return expenses within time window.
    summarize()
        Return summary of expenses grouped by type within window.
    load()
        Append the contents of a CSV file to the database.
    save()
        Save the current contents of the DB to a CSV file.
    clear()
        Remove all expenses from the DB.
    """

    def __init__(self):
        """Construct class instance."""
        CSTRING = "postgresql+psycopg"
        USER = "postgres"
        PASSWORD = ""
        HOST = "localhost"
        PORT = "5432"
        DATABASE = "sem-test" if os.environ.get("SEM_TEST") == "1" else "sem"

        DB = f"{CSTRING}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
        engine = create_engine(DB)
        if not database_exists(engine.url):
            create_database(engine.url)

        # Building schema
        Base.metadata.create_all(engine)

        self.db = Session(bind=engine)

    def close(self):
        """Close DB connection."""
        if self.db is not None:
            self.db.close()

    def add(self, data: ExpenseAdd):
        """Add expense to the DB.

        Parameters
        -----------------------
        data : ExpenseAdd
            Expense data.
        """
        # Primary key added automatically
        new_expense = Expense(**data.model_dump())
        self.db.add(new_expense)
        self.db.commit()
        self.db.refresh(new_expense)

    def query(self, params: QueryParameters) -> List[ExpenseRead]:
        """Return expenses in time window.

        Parameters
        -----------------------
        params : QueryParameters
            Parameters of the query.

        Returns
        -----------------------
        List[ExpenseRead]
            List of expenses matching the criteria.
        """
        if (params.start is None) or (params.end is None):
            date_condition = True
        else:
            date_condition = Expense.date.between(params.start, params.end)

        if params.types is None:
            type_condition = True
        else:
            type_condition = Expense.type.in_(params.types)

        if params.categories is None:
            cat_condition = True
        else:
            cat_condition = Expense.category.in_(params.categories)

        return self.db.scalars(
            select(Expense)
            .where(date_condition)
            .where(type_condition)
            .where(cat_condition)
            .order_by(Expense.date)
        ).all()

    def summarize(self, params: QueryParameters):
        """Return summary of expenses grouped by type within window.

        Parameters
        -----------------------
        params : QueryParameters
            Parameters of the query.

        Returns
        -----------------------
        List[Tuple[str, float]]
            List of `Tuple`s, each containing expense type and summed amounts.
        """
        if (params.start is None) or (params.end is None):
            date_condition = True
        else:
            date_condition = Expense.date.between(params.start, params.end)

        if params.types is None:
            type_condition = True
        else:
            type_condition = Expense.type.in_(params.types)

        if params.categories is None:
            cat_condition = True
        else:
            cat_condition = Expense.category.in_(params.categories)

        return self.db.execute(
            select(Expense.type, func.sum(Expense.amount))
            .where(date_condition)
            .where(type_condition)
            .where(cat_condition)
            .group_by(Expense.category, Expense.type)
            .order_by(Expense.category, Expense.type)
        ).all()

    def load(self, filename: str):
        """Append the contents of a CSV file to the database.

        The file should not contain headers, and have fields ordered as
        date -> type -> category -> amount -> description.

        Parameters
        -----------------------
        filename : str
            Filename of the input CSV file.
        """
        with open(filename, "r", newline="", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile, quotechar='"')

            for row in reader:
                self.db.add(
                    Expense(
                        date=str2date(row[0]),
                        type=row[1],
                        category=row[2],
                        amount=row[3],
                        description=row[4],
                    )
                )

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

    def clear(self):
        """Remove all expenses from the DB."""
        self.db.query(Expense).delete()
        # Resetting primary key
        self.db.execute(text("ALTER SEQUENCE expenses_id_seq RESTART"))
        self.db.commit()
