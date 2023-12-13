"""Types for CRUD operations.

Classes
-----------------------
ExpenseBase
    Base expense class.
ExpenseAdd
    Derived expense class for insertion operations.
ExpenseRead
    Derived expense class for query operations.
ExpenseUpdate
    Container for data to update existing expenses with.
QueryParameters
    Strong type for query parameters.
"""

# Copyright (c) 2023 Adriano Angelone
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# This file is part of sem-cli.
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

import datetime
from typing import Optional
from typing import List

from pydantic import BaseModel
from pydantic import Field


class ExpenseBase(BaseModel):
    """Base expense class.

    Attributes
    -----------------------
    date : datetime.date
        Date of the expense.
    type : str
        Low-level group of the expense.
    category : Optional[str]
        High-level group of the expense. Default is `None` -> "general".
    amount : float
        Amount of the expense.
    description : str
        Description of the expense.
    """

    date: datetime.date = Field(description="Date of the expense.")
    type: str = Field(description="Low-level group of the expense.")
    category: str = Field(
        default="",
        description="High-level group of the expense. Default is ''.",
    )
    amount: float = Field(description="Amount of the expense.")
    description: str = Field(description="Description of the expense.")


class ExpenseAdd(ExpenseBase):
    """Type for insertion operations."""


class ExpenseRead(ExpenseBase):
    """Type for selection operations.

    Attributes
    -----------------------
    id : int
        ID of the expense, primary key field.
    """

    id: int = Field(description="ID of the expense, primary key field.")


class ExpenseUpdate(BaseModel):
    """Container for data to update existing expenses with.

    Attributes set to `None` will not be changed.

    Attributes
    -----------------------
    date : Optional[datetime.date], default = None
        Date of the expense.
    type : Optional[str], default = None
        Low-level group of the expense.
    category : Optional[str], default = None
        High-level group of the expense.
    amount : Optional[float], default = None
        Amount of the expense.
    description : Optional[str], default = None
        Description of the expense.
    """

    date: Optional[datetime.date] = Field(
        default = None,
        description="Date of the expense.",
    )
    type: Optional[str] = Field(
        default=None,
        description="Low-level group of the expense.",
    )
    category: Optional[str] = Field(
        default=None,
        description="High-level group of the expense.",
    )
    amount: Optional[float] = Field(
        default=None,
        description="Amount of the expense.",
    )
    description: Optional[str] = Field(
        default=None,
        description="Description of the expense.",
    )


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

    start: Optional[datetime.date] = Field(
        default=None,
        description="""Query start date. If `None`, dates will not be used.
        Default is `None`.""",
    )
    end: Optional[datetime.date] = Field(
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
