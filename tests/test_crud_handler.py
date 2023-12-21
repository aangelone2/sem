# pylint: disable=redefined-outer-name
# required to avoid trouble with fixture declaration

"""Test module for crud handler."""

from fastapi.encoders import jsonable_encoder

from pytest import raises

from modules.schemas import ExpenseAdd
from modules.schemas import ExpenseRead
from modules.schemas import ExpenseUpdate
from modules.schemas import QueryParameters
from modules.crud_handler import CRUDHandlerError

from tests.common import expenses
from tests.common import str2date
from tests.common import CRUDHandlerTestContext


def test_global_query():
    """Tests no-parameter query."""
    with CRUDHandlerTestContext() as ch:
        # retrieve all expenses
        res = ch.query(QueryParameters())
        expected = [
            expenses[4],
            expenses[3],
            expenses[2],
            expenses[1],
            expenses[0],
        ]

        assert jsonable_encoder(res) == jsonable_encoder(expected)


def test_date_query():
    """Tests date-filtered query."""
    with CRUDHandlerTestContext() as ch:
        # only the 2 most recent expenses
        res = ch.query(
            QueryParameters(
                start="2023-12-05",
                end="2023-12-31",
            )
        )
        expected = [
            expenses[1],
            expenses[0],
        ]

        assert jsonable_encoder(res) == jsonable_encoder(expected)

        # use only start date
        res = ch.query(
            QueryParameters(
                start="2023-12-04",
            )
        )
        expected = [
            expenses[2],
            expenses[1],
            expenses[0],
        ]

        assert jsonable_encoder(res) == jsonable_encoder(expected)

        # use only end date
        res = ch.query(
            QueryParameters(
                end="2023-12-04",
            )
        )
        expected = [
            expenses[4],
            expenses[3],
            expenses[2],
        ]

        assert jsonable_encoder(res) == jsonable_encoder(expected)


def test_date_type_query():
    """Tests date- and type-filtered query."""
    with CRUDHandlerTestContext() as ch:
        # only the 2nd and 3rd most recent expenses, filtered by type and date
        res = ch.query(
            QueryParameters(
                start="2023-12-01",
                end="2023-12-31",
                types=["C", "M"],
            )
        )
        expected = [
            expenses[2],
            expenses[1],
        ]

        assert jsonable_encoder(res) == jsonable_encoder(expected)


def test_date_type_cat_query():
    """Tests date-, type-, and category-filtered query."""
    with CRUDHandlerTestContext() as ch:
        # only the 3rd most recent expense, filtered by type, category and date
        res = ch.query(
            QueryParameters(
                start="2023-12-01",
                end="2023-12-31",
                types=["C", "M"],
                categories=["trial", "nonexistent"],
            )
        )
        expected = [
            expenses[2],
        ]

        assert jsonable_encoder(res) == jsonable_encoder(expected)


def test_add():
    """Tests adding function."""
    with CRUDHandlerTestContext() as ch:
        # Auto-assign ID, default category, after only oldest expense
        new_exp = ExpenseAdd(
            date="2023-11-18",
            type="A",
            amount=-9.00,
            description="test expense",
        )

        ch.add(new_exp)

        # retrieve all expenses
        res = ch.query(QueryParameters())
        expected = [
            expenses[4],
            ExpenseRead(id=6, **new_exp.model_dump()),
            expenses[3],
            expenses[2],
            expenses[1],
            expenses[0],
        ]

        assert jsonable_encoder(res) == jsonable_encoder(expected)


def test_summarize():
    """Tests summarizing function."""
    with CRUDHandlerTestContext() as ch:
        ch.add(
            ExpenseAdd(
                date="2023-11-28",
                type="R",
                category="gen",
                amount=+1.00,
                description="test-2",
            )
        )
        ch.add(
            ExpenseAdd(
                date="2023-11-27",
                type="Q",
                category="test",
                amount=+1.00,
                description="test-3",
            )
        )
        ch.add(
            # Default category
            ExpenseAdd(
                date="2023-11-26",
                type="M",
                amount=+1.00,
                description="test-4",
            )
        )
        ch.add(
            ExpenseAdd(
                date="2023-12-06",
                type="R",
                category="gen",
                amount=+2.00,
                description="test-2",
            )
        )

        # No filtering
        res = ch.summarize(QueryParameters())
        assert jsonable_encoder(res) == {
            "gen": {"R": -9.0},
            "more": {"K": -15.0},
            "test": {"C": -13.0, "Q": +1.00, "T": -14.00},
            "trial": {"M": -13.5},
            "": {"M": +1.00},
        }

        # Type, category, and date filtering
        res = ch.summarize(
            QueryParameters(
                start="2023-12-05",
                end="2023-12-31",
                types=["R", "C"],
                categories=["gen", "test"],
            )
        )
        assert jsonable_encoder(res) == {
            "gen": {"R": -10.0},
            "test": {"C": -13.0},
        }


def test_load():
    """Tests loading function."""
    with CRUDHandlerTestContext() as ch:
        # Auto-assign ID, default category, after only oldest expense
        ch.load("resources/test-1.csv")

        # retrieve all expenses
        res = ch.query(QueryParameters())
        expected = [
            ExpenseRead(
                id=9,
                date="2021-12-09",
                type="T",
                category="",
                amount=-15.0,
                description="test-4",
            ),
            ExpenseRead(
                id=8,
                date="2022-12-10",
                type="L",
                category="",
                amount=-14.0,
                description="test-3",
            ),
            expenses[4],
            expenses[3],
            expenses[2],
            ExpenseRead(
                id=6,
                date="2023-12-12",
                type="G",
                category="",
                amount=-12.0,
                description="test-1",
            ),
            expenses[1],
            expenses[0],
            ExpenseRead(
                id=7,
                date="2026-12-11",
                type="K",
                category="",
                amount=-13.0,
                description="test-2",
            ),
        ]

        assert jsonable_encoder(res) == jsonable_encoder(expected)

        # Nonexistent file
        with raises(FileNotFoundError) as err:
            ch.load("resources/test-missing.csv")
        assert str(err.value) == "resources/test-missing.csv not found"

        # Checking that no changes are commited in case of error
        res = ch.query(QueryParameters())
        assert jsonable_encoder(res) == jsonable_encoder(expected)

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
        assert jsonable_encoder(res) == jsonable_encoder(expected)

        # Row with invalid field
        with raises(CRUDHandlerError) as err:
            ch.load("resources/test-invalid_field.csv")
        assert str(err.value) == (
            "resources/test-invalid_field.csv :: 2 :: invalid field"
        )

        # Checking that no changes are committed in case of error
        res = ch.query(QueryParameters())
        assert jsonable_encoder(res) == jsonable_encoder(expected)


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
        ch.update(3, ExpenseUpdate(date="2028-05-01"))
        ch.update(1, ExpenseUpdate(type="P", amount=+10.0))

        # retrieve all expenses
        res = ch.query(QueryParameters())

        exp3 = expenses[2].model_copy(deep=True)
        exp3.date = str2date("2028-05-01")

        exp1 = expenses[0].model_copy(deep=True)
        exp1.type = "P"
        exp1.amount = +10.0

        expected = [
            expenses[4],
            expenses[3],
            expenses[1],
            exp1,
            exp3,
        ]

        assert jsonable_encoder(res) == jsonable_encoder(expected)

        # Nonexistent ID
        with raises(CRUDHandlerError) as err:
            res = ch.update(19, ExpenseUpdate(type="QQ"))
        assert str(err.value) == "ID 19 not found"

        # Checking that no changes are committed in case of error
        res = ch.query(QueryParameters())
        assert jsonable_encoder(res) == jsonable_encoder(expected)


def test_remove():
    """Tests removal function."""
    with CRUDHandlerTestContext() as ch:
        # Selective removal
        ch.remove([3, 1])

        res = ch.query(QueryParameters())
        expected = [
            expenses[4],
            expenses[3],
            expenses[1],
        ]

        assert jsonable_encoder(res) == jsonable_encoder(expected)

        # Nonexistent ID
        with raises(CRUDHandlerError) as err:
            res = ch.remove([19])
        assert str(err.value) == "ID 19 not found"

        # Checking that no changes are committed in case of error
        res = ch.query(QueryParameters())
        assert jsonable_encoder(res) == jsonable_encoder(expected)

        # Complete removal
        ch.erase()
        assert not ch.query(QueryParameters())
