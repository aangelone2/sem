# pylint: disable=redefined-outer-name
# required to avoid trouble with fixture declaration

"""Test module for crud handler."""


from datetime import datetime

import pytest

from modules.schemas import expense_add
from modules.crud import crud_handler


@pytest.fixture
def fix_db():
    """DB fixture."""

    # in-memory DB for testing, easier cleanup
    ch = crud_handler("")

    # adding test data
    lyear = [2023, 2023, 2023, 2023]
    lmonth = [12, 12, 12, 11]
    lday = [31, 15, 1, 15]
    ltype = ["R", "C", "T", "K"]
    lamount = [-12.0, -13.0, -14.0, -15.0]
    ljustification = ["test-1", "test-2", "test-3", "test-4"]

    for y, m, d, t, a, j in zip(
        lyear, lmonth, lday, ltype, lamount, ljustification
    ):
        ch.add(
            expense_add(
                date=datetime(y, m, d),
                type=t,
                amount=a,
                justification=j,
            )
        )

    return ch


def test_query(fix_db):
    """Tests for `query()` function."""

    # should retrieve all expenses
    res = fix_db.query()
    assert len(res) == 4
    assert res[0].date == datetime(2023, 11, 15)

    # only the 2 most recent expenses
    res = fix_db.query(
        datetime(2023, 12, 2), datetime(2023, 12, 31)
    )
    assert len(res) == 2
    assert res[0].date == datetime(2023, 12, 15)
    assert res[0].type == "C"
    assert res[1].date == datetime(2023, 12, 31)
    assert res[1].type == "R"
