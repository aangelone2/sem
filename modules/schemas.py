"""Types for CRUD operations.

Classes
-----------------------
ExpenseBase
    Base expense class.
ExpenseAdd
    Derived expense class for insertion operations.
class ExpenseRead
    Derived expense class for query operations.
"""

# Copyright (c) 2023 Adriano Angelone
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the
# Software.
#
# This file is part of sem.
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
from pydantic import BaseModel


class ExpenseBase(BaseModel):
    """Base expense class.

    Attributes
    -----------------------
    date : date
        Date of the expense
    type : str
        Char representing the expense type
    amount : float
        Amount of the expense
    justification : str
        Justification for the expense
    """

    date: date
    # FIXME impose length 1
    type: str
    amount: float
    justification: str


class ExpenseAdd(ExpenseBase):
    """Expense for insertion operations."""


class ExpenseRead(ExpenseBase):
    """Expense for selection operations.

    Attributes
    -----------------------
    id : int
        Expense ID (primary key)
    """

    id: int
