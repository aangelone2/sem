# pylint: disable=redefined-outer-name
# required to avoid trouble with fixture declaration

"""Test module for crud handler."""


from pytest import approx
from pytest import raises

from modules.schemas import ExpenseAdd
from modules.schemas import ExpenseUpdate
from modules.crud_handler import str2date
from modules.crud_handler import QueryParameters
from modules.crud_handler import CRUDHandlerError

from tests.common import CRUDHandlerTestContext


def test_global_query():
    """Tests no-parameter query."""

    with CRUDHandlerTestContext() as ch:
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
            "more",
            "test",
            "trial",
            "test",
            "gen",
        ]
        assert [approx(r.amount) for r in res] == [
            -15.0,
            -14.0,
            -13.5,
            -13.0,
            -12.0,
        ]
        assert [r.description for r in res] == [
            "test-4",
            "test-3",
            "test-2.5",
            "test-2",
            "test-1",
        ]


def test_date_query():
    """Tests date-filtered query."""

    with CRUDHandlerTestContext() as ch:
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

    with CRUDHandlerTestContext() as ch:
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

    with CRUDHandlerTestContext() as ch:
        # only the 3rd most recent expense, filtered by type, category and date
        res = ch.query(
            QueryParameters(
                start=str2date("2023-12-01"),
                end=str2date("2023-12-31"),
                types=["C", "M"],
                categories=["trial", "nonexistent"],
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

    with CRUDHandlerTestContext() as ch:
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
            "more",
            "",
            "test",
            "trial",
            "test",
            "gen",
        ]
        assert [approx(r.amount) for r in res] == [
            -15.0,
            -9.0,
            -14.0,
            -13.5,
            -13.0,
            -12.0,
        ]
        assert [r.description for r in res] == [
            "test-4",
            "test expense",
            "test-3",
            "test-2.5",
            "test-2",
            "test-1",
        ]


def test_load():
    """Tests loading function."""

    with CRUDHandlerTestContext() as ch:
        # Auto-assign ID, default category, after only oldest expense
        ch.load("resources/test-1.csv")

        # retrieve all expenses
        res = ch.query(QueryParameters())

        assert [r.id for r in res] == [9, 8, 5, 4, 3, 6, 2, 1, 7]
        assert [r.date for r in res] == [
            str2date("2021-12-09"),
            str2date("2022-12-10"),
            str2date("2023-11-15"),
            str2date("2023-12-01"),
            str2date("2023-12-04"),
            str2date("2023-12-12"),
            str2date("2023-12-15"),
            str2date("2023-12-31"),
            str2date("2026-12-11"),
        ]
        assert [r.type for r in res] == [
            "T",
            "L",
            "K",
            "T",
            "M",
            "G",
            "C",
            "R",
            "K",
        ]
        assert [r.category for r in res] == [
            "",
            "",
            "more",
            "test",
            "trial",
            "",
            "test",
            "gen",
            "",
        ]
        assert [approx(r.amount) for r in res] == [
            -15.0,
            -14.0,
            -15.0,
            -14.0,
            -13.5,
            -12.0,
            -13.0,
            -12.0,
            -13.0,
        ]
        assert [r.description for r in res] == [
            "test-4",
            "test-3",
            "test-4",
            "test-3",
            "test-2.5",
            "test-1",
            "test-2",
            "test-1",
            "test-2",
        ]

        # Nonexistent file
        with raises(FileNotFoundError) as err:
            ch.load("resources/test-missing.csv")
        assert str(err.value) == "resources/test-missing.csv not found"

        # Checking that no changes are commited in case of error
        res = ch.query(QueryParameters())
        assert len(res) == 9

        # Row with invalid field number
        # fmt: off
        with raises(CRUDHandlerError) as err:
            ch.load("resources/test-invalid_field_number.csv")
        assert str(err.value) == (
            "resources/test-invalid_field_number.csv"
            " :: 3"
            " :: invalid field number"
        )
        # fmt: on

        # Checking that no changes are committed in case of error
        res = ch.query(QueryParameters())
        assert len(res) == 9

        # Row with invalid field
        with raises(CRUDHandlerError) as err:
            ch.load("resources/test-invalid_field.csv")
        assert str(err.value) == (
            "resources/test-invalid_field.csv :: 2 :: invalid field"
        )

        # Checking that no changes are committed in case of error
        res = ch.query(QueryParameters())
        assert len(res) == 9


def test_save(tmpdir):
    """Tests saving function."""

    with CRUDHandlerTestContext() as ch:
        # Temporary file
        file = tmpdir.join("test-2.csv")
        ch.save(file.strpath)

        rows = file.readlines()

        assert len(rows) == 5
        assert rows[0] == '"2023-11-15","K","more",-15.0,"test-4"\n'
        assert rows[1] == '"2023-12-01","T","test",-14.0,"test-3"\n'
        assert rows[2] == '"2023-12-04","M","trial",-13.5,"test-2.5"\n'
        assert rows[3] == '"2023-12-15","C","test",-13.0,"test-2"\n'
        assert rows[4] == '"2023-12-31","R","gen",-12.0,"test-1"\n'



def test_update():
    """Tests updating function."""

    with CRUDHandlerTestContext() as ch:
        ch.update(3, ExpenseUpdate(date=str2date("2028-05-01")))
        ch.update(1, ExpenseUpdate(type="P", amount=+10.00))

        # retrieve all expenses
        res = ch.query(QueryParameters())

        assert [r.id for r in res] == [5, 4, 2, 1, 3]
        assert [r.date for r in res] == [
            str2date("2023-11-15"),
            str2date("2023-12-01"),
            str2date("2023-12-15"),
            str2date("2023-12-31"),
            str2date("2028-05-01"),
        ]
        assert [r.type for r in res] == ["K", "T", "C", "P", "M"]
        assert [r.category for r in res] == [
            "more",
            "test",
            "test",
            "gen",
            "trial",
        ]
        assert [approx(r.amount) for r in res] == [
            -15.0,
            -14.0,
            -13.0,
            +10.0,
            -13.5,
        ]
        assert [r.description for r in res] == [
            "test-4",
            "test-3",
            "test-2",
            "test-1",
            "test-2.5",
        ]

        # Nonexistent ID
        with raises(CRUDHandlerError) as err:
            res = ch.update(19, ExpenseUpdate(type="QQ"))
        assert str(err.value) == "ID 19 not found"

        # Checking that no changes are committed in case of error
        res = ch.query(QueryParameters())
        assert len(res) == 5


def test_remove():
    """Tests removal function."""

    with CRUDHandlerTestContext() as ch:
        # Selective removal
        ch.remove([3, 1])

        res = ch.query(QueryParameters())

        assert [r.id for r in res] == [5, 4, 2]
        assert [r.date for r in res] == [
            str2date("2023-11-15"),
            str2date("2023-12-01"),
            str2date("2023-12-15"),
        ]
        assert [r.type for r in res] == ["K", "T", "C"]
        assert [r.category for r in res] == [
            "more",
            "test",
            "test",
        ]
        assert [approx(r.amount) for r in res] == [
            -15.0,
            -14.0,
            -13.0,
        ]
        assert [r.description for r in res] == [
            "test-4",
            "test-3",
            "test-2",
        ]

        # Nonexistent ID
        with raises(CRUDHandlerError) as err:
            res = ch.remove([19])
        assert str(err.value) == "ID 19 not found"

        # Checking that no changes are committed in case of error
        res = ch.query(QueryParameters())
        assert len(res) == 3

        # Complete removal
        ch.remove()
        assert not ch.query(QueryParameters())
