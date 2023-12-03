# pylint: disable=redefined-outer-name
# required to avoid trouble with fixture declaration

"""Common testing utilities."""


from modules.schemas import ExpenseAdd
from modules.crud_handler import str2date
from modules.crud_handler import CRUDHandler


def populate_ch(ch: CRUDHandler):
    """Populate a passed CRUDHandler with expenses."""
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

    return ch
