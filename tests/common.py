# pylint: disable=redefined-outer-name
# required to avoid trouble with fixture declaration

"""Common testing utilities."""


from contextlib import contextmanager

from modules.schemas import ExpenseAdd
from modules.crud_handler import str2date
from modules.crud_handler import CRUDHandler


@contextmanager
def CRUDHandlerTestContext():
    """Context management function for CRUDHandler testing.

    Inints and inserts example data, removing all data from table at closure.

    Yields
    -----------------------
    CRUDHandler
        The context-managed and populated CRUDHandler.
    """
    ch = CRUDHandler()
    ch.remove()

    # adding test data
    ldate = [
        "2023-12-31",
        "2023-12-15",
        "2023-12-04",
        "2023-12-01",
        "2023-11-15",
    ]
    ltype = ["R", "C", "M", "T", "K"]
    lcat = ["gen", "test", "trial", "test", "more"]
    lamount = [-12.0, -13.0, -13.5, -14.0, -15.0]
    ldesc = ["test-1", "test-2", "test-2.5", "test-3", "test-4"]

    for d, t, c, a, j in zip(ldate, ltype, lcat, lamount, ldesc):
        ch.add(
            ExpenseAdd(
                date=str2date(d),
                type=t,
                category=c,
                amount=a,
                description=j,
            )
        )

    try:
        yield ch
    finally:
        ch.remove()
        ch.close()
