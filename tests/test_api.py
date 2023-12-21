# pylint: disable=redefined-outer-name,unused-import,duplicate-code
# required to avoid trouble with fixture declaration

"""Test module for API."""

from fastapi.testclient import TestClient
from fastapi.encoders import jsonable_encoder

import pytest

from modules.schemas import ExpenseRead
from modules.crud_handler import CRUDHandler
from modules.crud_handler import CRUDHandlerContext
from modules.api import app
from modules.api import get_ch

from tests.common import TEST_DB_NAME
from tests.common import str2date
from tests.common import expenses
from tests.common import CRUDHandlerTestContext


def get_test_ch() -> CRUDHandler:
    """Yield CRUDHandler object for testing purposes.

    Pre-populated with some expenses, linked to "sem-test" DB.

    Yields
    -----------------------
    CRUDHandler
        The CRUDHandler object.
    """
    with CRUDHandlerContext(TEST_DB_NAME) as ch:
        yield ch


@pytest.fixture
def test_client():
    """Construct FastAPI test client."""
    app.dependency_overrides[get_ch] = get_test_ch
    return TestClient(app)


def test_root(test_client):
    """Test main page."""
    response = test_client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "homepage reached"}


def test_global_query_api(test_client):
    """Tests unfiltered query."""
    with CRUDHandlerTestContext():
        response = test_client.get("/query")

        expected = [
            expenses[4],
            expenses[3],
            expenses[2],
            expenses[1],
            expenses[0],
        ]

        assert response.status_code == 200
        assert response.json() == jsonable_encoder(expected)


def test_date_query_api(test_client):
    """Tests date-filtered query."""
    with CRUDHandlerTestContext():
        # fmt: off
        response = test_client.get(
            "/query"
            "?start=2023-12-05"
            "&end=2023-12-31"
        )
        # fmt: on

        expected = [
            expenses[1],
            expenses[0],
        ]

        assert response.status_code == 200
        assert response.json() == jsonable_encoder(expected)

        # use only start date
        response = test_client.get("/query?start=2023-12-04")
        expected = [
            expenses[2],
            expenses[1],
            expenses[0],
        ]

        assert response.status_code == 200
        assert response.json() == jsonable_encoder(expected)

        # use only end date
        response = test_client.get("/query?end=2023-12-04")
        expected = [
            expenses[4],
            expenses[3],
            expenses[2],
        ]

        assert response.status_code == 200
        assert response.json() == jsonable_encoder(expected)


def test_date_type_query_api(test_client):
    """Tests date- and type-filtered query."""
    with CRUDHandlerTestContext():
        response = test_client.get(
            "/query"
            "?start=2023-12-01"
            "&end=2023-12-31"
            "&types=C"
            "&types=M"
        )

        expected = [
            expenses[2],
            expenses[1],
        ]

        assert response.status_code == 200
        assert response.json() == jsonable_encoder(expected)


def test_date_type_cat_query_api(test_client):
    """Tests date-, type-, and category-filtered query."""
    with CRUDHandlerTestContext():
        response = test_client.get(
            "/query"
            "?start=2023-12-01"
            "&end=2023-12-31"
            "&types=C"
            "&types=M"
            "&categories=trial"
            "&categories=nonexistent"
        )

        expected = [
            expenses[2],
        ]

        assert response.status_code == 200
        assert response.json() == jsonable_encoder(expected)


def test_add_api(test_client):
    """Tests adding function."""
    with CRUDHandlerTestContext():
        # Skipping category
        new_exp = {
            "date": "2023-12-12",
            "type": "M",
            "amount": -1.44,
            "description": "added via API",
        }
        response = test_client.post("/add", json=new_exp)

        assert response.status_code == 200
        assert response.json() == {"message": "expense added"}

        response = test_client.get("/query?types=M")

        expected = [
            expenses[2],
            ExpenseRead(id=6, **new_exp),
        ]

        assert response.status_code == 200
        assert response.json() == jsonable_encoder(expected)


def test_summarize_api(test_client):
    """Tests summarizing function."""
    with CRUDHandlerTestContext():
        response = test_client.post(
            "/add",
            json={
                "date": "2023-11-28",
                "type": "R",
                "category": "gen",
                "amount": +1.00,
                "description": "test-2",
            },
        )
        assert response.status_code == 200
        assert response.json() == {"message": "expense added"}

        response = test_client.post(
            "/add",
            json={
                "date": "2023-11-27",
                "type": "Q",
                "category": "test",
                "amount": +1.00,
                "description": "test-3",
            },
        )
        assert response.status_code == 200
        assert response.json() == {"message": "expense added"}

        # Default category
        response = test_client.post(
            "/add",
            json={
                "date": "2023-11-26",
                "type": "M",
                "amount": +1.00,
                "description": "test-4",
            },
        )
        assert response.status_code == 200
        assert response.json() == {"message": "expense added"}

        response = test_client.post(
            "/add",
            json={
                "date": "2023-12-06",
                "type": "R",
                "category": "gen",
                "amount": +2.00,
                "description": "test-2",
            },
        )
        assert response.status_code == 200
        assert response.json() == {"message": "expense added"}

        # No filtering
        response = test_client.get("/summarize")
        assert response.status_code == 200
        assert response.json() == {
            "gen": {"R": -9.0},
            "more": {"K": -15.0},
            "test": {"C": -13.0, "Q": +1.00, "T": -14.00},
            "trial": {"M": -13.5},
            "": {"M": +1.00},
        }

        # Type, category, and date filtering
        # fmt: off
        response = test_client.get(
            "/summarize"
            "?start=2023-12-05"
            "&end=2023-12-31"
            "&types=R"
            "&types=C"
            "&categories=gen"
            "&categories=test"
        )
        # fmt: on
        assert response.status_code == 200
        assert response.json() == {
            "gen": {"R": -10.0},
            "test": {"C": -13.0},
        }


def test_load_api(test_client):
    """Tests loading function."""
    with CRUDHandlerTestContext():
        # fmt: off
        response = test_client.post(
            "/load"
            "?csvfile=resources/test-1.csv"
        )
        # fmt: on
        assert response.status_code == 200
        assert response.json() == {"message": "file loaded"}

        # retrieve all expenses
        response = test_client.get("/query")

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

        assert response.status_code == 200
        assert response.json() == jsonable_encoder(expected)

        # Nonexistent file
        response = test_client.post("/load?csvfile=resources/test-missing.csv")

        assert response.status_code == 404
        assert response.json() == {
            "detail": "resources/test-missing.csv not found"
        }

        # Invalid field number
        response = test_client.post(
            "/load?csvfile=resources/test-invalid_field_number.csv"
        )

        assert response.status_code == 422
        # fmt: off
        assert response.json() == {
            "detail": (
                "resources/test-invalid_field_number.csv"
                " :: 3"
                " :: invalid field number"
            )
        }
        # fmt: on

        # Row with invalid field
        response = test_client.post(
            "/load?csvfile=resources/test-invalid_field.csv"
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": "resources/test-invalid_field.csv :: 2 :: invalid field"
        }


def test_save_api(test_client, tmpdir):
    """Tests saving function."""
    with CRUDHandlerTestContext():
        file = tmpdir.join("test-2.csv")
        # fmt:off
        response = test_client.get(
            "/save"
            f"?csvfile={file.strpath}"
        )

        assert response.status_code == 200
        assert response.json() == {"message": "file saved"}

        rows = file.readlines()

        assert len(rows) == 5
        assert rows[0] == '"2023-11-15","K","more",-15.0,"test-4"\n'
        assert rows[1] == '"2023-12-01","T","test",-14.0,"test-3"\n'
        assert rows[2] == '"2023-12-04","M","trial",-13.5,"test-2.5"\n'
        assert rows[3] == '"2023-12-15","C","test",-13.0,"test-2"\n'
        assert rows[4] == '"2023-12-31","R","gen",-12.0,"test-1"\n'


def test_update_api(test_client):
    """Tests updating request."""
    with CRUDHandlerTestContext():
        response = test_client.patch(
            "/update/?ID=3",
            json={
                "date": "2028-05-01",
            },
        )
        assert response.status_code == 200
        assert response.json() == {"message": "expense updated"}

        response = test_client.patch(
            "/update/?ID=1",
            json={
                "type": "P",
                "amount": +10.00,
            },
        )
        assert response.status_code == 200
        assert response.json() == {"message": "expense updated"}

        response = test_client.get("/query")

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

        assert response.status_code == 200
        assert response.json() == jsonable_encoder(expected)

        # Inexistent ID
        response = test_client.patch(
            "/update/?ID=19",
            json={
                "date": "2028-05-01",
            },
        )
        assert response.status_code == 404
        assert response.json() == {"detail": "ID 19 not found"}


def test_remove_api(test_client):
    """Tests removing request."""
    with CRUDHandlerTestContext():
        # Selective removal
        response = test_client.delete("/remove?ids=3&ids=1")

        assert response.status_code == 200
        assert response.json() == {"message": "expense(s) removed"}

        response = test_client.get("/query")

        expected = [
            expenses[4],
            expenses[3],
            expenses[1],
        ]

        assert response.json() == jsonable_encoder(expected)

        # Inexistent ID
        response = test_client.delete("/remove/?ids=19")
        assert response.status_code == 404
        assert response.json() == {"detail": "ID 19 not found"}

        # Complete removal
        response = test_client.delete("/erase")

        assert response.status_code == 200
        assert response.json() == {"message": "database erased"}

        response = test_client.get("/query")
        assert not response.json()
