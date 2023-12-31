# pylint: disable=redefined-outer-name
# required to avoid trouble with fixture declaration

"""Common testing utilities."""


from datetime import datetime

from contextlib import contextmanager

from modules.schemas import ExpenseAdd
from modules.schemas import ExpenseRead
from modules.crud_handler import CRUDHandler


TEST_DB_NAME = "sem-test"


# Example expenses for testing
expenses = (
    ExpenseRead(
        id=1,
        date="2023-12-31",
        type="R",
        category="gen",
        amount=-12.0,
        description="test-1",
    ),
    ExpenseRead(
        id=2,
        date="2023-12-15",
        type="C",
        category="test",
        amount=-13.0,
        description="test-2",
    ),
    ExpenseRead(
        id=3,
        date="2023-12-04",
        type="M",
        category="trial",
        amount=-13.5,
        description="test-2.5",
    ),
    ExpenseRead(
        id=4,
        date="2023-12-01",
        type="T",
        category="test",
        amount=-14.0,
        description="test-3",
    ),
    ExpenseRead(
        id=5,
        date="2023-11-15",
        type="K",
        category="more",
        amount=-15.0,
        description="test-4",
    ),
)


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


@contextmanager
def CRUDHandlerTestContext() -> CRUDHandler:
    """Manage testing context for CRUDHandler.

    Inits and inserts example data, removing all data from table at closure.

    Yields
    -----------------------
    CRUDHandler
        The context-managed and populated CRUDHandler.
    """
    # Easier to define a new context manager,
    # should call erase() in __enter__() and __exit__().
    ch = CRUDHandler(TEST_DB_NAME)
    ch.erase()

    for exp in expenses:
        # ID field ignored by pydantic constructor
        ch.add(ExpenseAdd(**exp.model_dump()))

    try:
        yield ch
    finally:
        ch.erase()
        ch.close()
