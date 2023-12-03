# pylint: disable=redefined-outer-name
# required to avoid trouble with fixture declaration

"""Test module for crud handler."""


from pytest import approx

from modules.schemas import ExpenseAdd
from modules.crud_handler import str2date
from modules.crud_handler import CRUDHandlerContext
from modules.crud_handler import QueryParameters

from tests.common import populate_ch


def test_global_query():
    """Tests no-parameter query."""

    with CRUDHandlerContext() as ch:
        populate_ch(ch)

        # retrieve all expenses
        res = ch.query(QueryParameters())

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


def test_date_query():
    """Tests date-filtered query."""

    with CRUDHandlerContext() as ch:
        populate_ch(ch)

        # only the 2 most recent expenses
        res = ch.query(
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


def test_date_type_query():
    """Tests date- and type-filtered query."""

    with CRUDHandlerContext() as ch:
        populate_ch(ch)

        # only the 2nd and 3rd most recent expenses, filtered by type and date
        res = ch.query(
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


def test_date_type_cat_query():
    """Tests date-, type-, and category-filtered query."""

    with CRUDHandlerContext() as ch:
        populate_ch(ch)

        # only the 3rd most recent expense, filtered by type, category and date
        res = ch.query(
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



def test_add():
    """Tests adding function."""

    with CRUDHandlerContext() as ch:
        populate_ch(ch)

        # Auto-assign ID, default category, after only oldest expense
        ch.add(
            ExpenseAdd(
                date=str2date("2023-11-18"),
                type="A",
                amount=-9.00,
                description="test expense",
            )
        )

        # retrieve all expenses
        res = ch.query(QueryParameters())

        assert [r.id for r in res] == [5, 6, 4, 3, 2, 1]
        assert [r.date for r in res] == [
            str2date("2023-11-15"),
            str2date("2023-11-18"),
            str2date("2023-12-01"),
            str2date("2023-12-04"),
            str2date("2023-12-15"),
            str2date("2023-12-31"),
        ]
        assert [r.type for r in res] == ["K", "A", "T", "M", "C", "R"]
        assert [r.category for r in res] == [
            "more", "", "test", "trial", "test", "gen"
        ]
        assert [approx(r.amount) for r in res] == [
            -15.0, -9.00, -14.0, -13.5, -13.0, -12.0
        ]
        assert [r.description for r in res] == [
            "test-4", "test expense", "test-3", "test-2.5", "test-2", "test-1"
        ]
