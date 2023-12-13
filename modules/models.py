"""Database mapped class.

Classes
-----------------------
Base
    Inherits DeclarativeBase, base class for mapped objects.
Expense
    Class modeling database entry.
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
        ID of the expense, primary key field.
    date : date
        Date of the expense.
    type : str
        Low-level group of the expense.
    category : str
        High-level group of the expense. Default is "".
    amount : float
        Amount of the expense.
    description : str
        Description of the expense.
    """

    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date]
    type: Mapped[str]
    category: Mapped[str] = mapped_column(default="")
    amount: Mapped[float]
    description: Mapped[str]

    def __repr__(self) -> str:
        """Dunder representation method."""
        return f"""Expense(
            id={self.id!r},
            date={self.date!r},
            type={self.type!r},
            category={self.category!r},
            amount={self.amount!r},
            description={self.description!r}
        )"""
