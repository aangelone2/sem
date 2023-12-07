# pylint: disable=redefined-outer-name
# required to avoid trouble with fixture declaration

"""Common testing utilities."""


from contextlib import contextmanager

from modules.schemas import ExpenseAdd
from modules.schemas import ExpenseRead
from modules.crud_handler import str2date
from modules.crud_handler import CRUDHandler


# Example expenses for testing
expenses = (
    ExpenseRead(
        id=1,
        date=str2date("2023-12-31"),
        type="R",
        category="gen",
        amount=-12.0,
        description="test-1",
    ),
    ExpenseRead(
        id=2,
        date=str2date("2023-12-15"),
        type="C",
        category="test",
        amount=-13.0,
        description="test-2",
    ),
    ExpenseRead(
        id=3,
        date=str2date("2023-12-04"),
        type="M",
        category="trial",
        amount=-13.5,
        description="test-2.5",
    ),
    ExpenseRead(
        id=4,
        date=str2date("2023-12-01"),
        type="T",
        category="test",
        amount=-14.0,
        description="test-3",
    ),
    ExpenseRead(
        id=5,
        date=str2date("2023-11-15"),
        type="K",
        category="more",
        amount=-15.0,
        description="test-4",
    ),
)


@contextmanager
def CRUDHandlerTestContext():
    """Context management function for CRUDHandler testing.

    Inits and inserts example data, removing all data from table at closure.

    Yields
    -----------------------
    CRUDHandler
        The context-managed and populated CRUDHandler.
    """
    ch = CRUDHandler()
    ch.remove()

    for exp in expenses:
        # ID field ignored by pydantic constructor
        ch.add(ExpenseAdd(**exp.model_dump()))

    try:
        yield ch
    finally:
        ch.remove()
        ch.close()
