# pylint: disable=redefined-outer-name
# required to avoid trouble with fixture declaration

"""Test module for crud handler."""


import pytest
from pytest import approx

from modules.schemas import ExpenseAdd
from modules.crud_handler import str2date
from modules.crud_handler import CRUDHandler
from modules.crud_handler import QueryParameters


@pytest.fixture
def fix_db():
    """DB fixture."""

    ch = CRUDHandler()
    # in-memory DB for testing, easier cleanup
    ch.access()

    # adding test data
    ldate = [
        "2023-12-31", "2023-12-15", "2023-12-04", "2023-12-01", "2023-11-15"
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


def test_global_query(fix_db):
    """Tests no-parameter query."""

    # retrieve all expenses
    res = fix_db.query(QueryParameters())

    assert [r.id for r in res] == [5, 4, 3, 2, 1]
    assert [r.date for r in res] == [
        str2date("2023-11-15"),
        str2date("2023-12-01"),
        str2date("2023-12-04"),
        str2date("2023-12-15"),
        str2date("2023-12-31"),
    ]
    assert [r.type for r in res] == ["K", "T", "M", "C", "R"]
    assert [r.category for r in res] == [
        "more", "test", "trial", "test", "gen"
    ]
    assert [approx(r.amount) for r in res] == [
        -15.0, -14.0, -13.5, -13.0, -12.0
    ]
    assert [r.description for r in res] == [
        "test-4", "test-3", "test-2.5", "test-2", "test-1"
    ]


def test_date_query(fix_db):
    """Tests date-filtered query."""

    # only the 2 most recent expenses
    res = fix_db.query(
        QueryParameters(
            start=str2date("2023-12-05"),
            end=str2date("2023-12-31"),
        )
    )
    assert [r.id for r in res] == [2, 1]
    assert [r.date for r in res] == [
        str2date("2023-12-15"),
        str2date("2023-12-31"),
    ]
    assert [r.type for r in res] == ["C", "R"]
    assert [r.category for r in res] == ["test", "gen"]
    assert [approx(r.amount) for r in res] == [-13.0, -12.0]
    assert [r.description for r in res] == ["test-2", "test-1"]


def test_date_type_query(fix_db):
    """Tests date- and type-filtered query."""

    # only the 2nd and 3rd most recent expenses, filtered by type and date
    res = fix_db.query(
        QueryParameters(
            start=str2date("2023-12-01"),
            end=str2date("2023-12-31"),
            types=["C", "M"],
        )
    )
    assert [r.id for r in res] == [3, 2]
    assert [r.date for r in res] == [
        str2date("2023-12-04"),
        str2date("2023-12-15"),
    ]
    assert [r.type for r in res] == ["M", "C"]
    assert [r.category for r in res] == ["trial", "test"]
    assert [approx(r.amount) for r in res] == [-13.5, -13.0]
    assert [r.description for r in res] == ["test-2.5", "test-2"]


def test_date_type_cat_query(fix_db):
    """Tests date-, type-, and category-filtered query."""

    # only the 3rd most recent expense, filtered by type, category and date
    res = fix_db.query(
        QueryParameters(
            start=str2date("2023-12-01"),
            end=str2date("2023-12-31"),
            types=["C", "M"],
            categories=["trial", "nonexistent"]
        )
    )
    assert [r.id for r in res] == [3]
    assert [r.date for r in res] == [str2date("2023-12-04")]
    assert [r.type for r in res] == ["M"]
    assert [r.category for r in res] == ["trial"]
    assert [approx(r.amount) for r in res] == [-13.5]
    assert [r.description for r in res] == ["test-2.5"]
