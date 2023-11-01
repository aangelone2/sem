"""Types for CRUD operations.

Classes
-----------------------
ExpenseBase
    Base expense class.
ExpenseAdd
    Derived expense class for insertion operations.
ExpenseRead
    Derived expense class for query operations.
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
    category: Optional[str] = Field(
        default=None,
        description="High-level group of the expense. Default is `None`.",
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
