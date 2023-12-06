# pylint: disable=redefined-outer-name,unused-import,duplicate-code
# required to avoid trouble with fixture declaration

"""Test module for API."""

from typing import Dict

import pytest
from pytest import approx
from fastapi.testclient import TestClient

from modules.api import app
from modules.crud_handler import str2date
from modules.crud_handler import QueryParameters

from tests.common import CRUDHandlerTestContext


TEST_DB_PATH = "resources/test.sqlite"


def approx_dict(d1: Dict, d2: Dict) -> bool:
    """Compare dictionaries with floating-point values.

    Compares (recursively) the two passed dictionaries,
    using pytest.approx() in case the values are python
    or numpy floating points.

    Parameters
    -----------------------
    d1, d2 : Dict
        The dictionaries to compare

    Returns
    -----------------------
    bool
        Whether or not the arguments are approx. equal
    """
    if d1.keys() != d2.keys():
        return False

    for k in d1.keys():
        if isinstance(d1[k], float):
            if d2[k] != approx(d1[k]):
                return False
        elif isinstance(d1[k], dict):
            if not approx_dict(d1[k], d2[k]):
                return False
        else:
            if d2[k] != d1[k]:
                return False

    return True


@pytest.fixture
def test_client():
    """Construct FastAPI test client."""
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

        assert response.status_code == 200
        assert len(response.json()) == 5

        expected = [
            {
                "id": 5,
                "date": "2023-11-15",
                "type": "K",
                "category": "more",
                "amount": -15.0,
                "description": "test-4",
            },
            {
                "id": 4,
                "date": "2023-12-01",
                "type": "T",
                "category": "test",
                "amount": -14.0,
                "description": "test-3",
            },
            {
                "id": 3,
                "date": "2023-12-04",
                "type": "M",
                "category": "trial",
                "amount": -13.5,
                "description": "test-2.5",
            },
            {
                "id": 2,
                "date": "2023-12-15",
                "type": "C",
                "category": "test",
                "amount": -13.0,
                "description": "test-2",
            },
            {
                "id": 1,
                "date": "2023-12-31",
                "type": "R",
                "category": "gen",
                "amount": -12.0,
                "description": "test-1",
            },
        ]

        for r, e in zip(response.json(), expected):
            assert approx_dict(r, e)


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

        assert response.status_code == 200
        assert len(response.json()) == 2

        expected = [
            {
                "id": 2,
                "date": "2023-12-15",
                "type": "C",
                "category": "test",
                "amount": -13.0,
                "description": "test-2",
            },
            {
                "id": 1,
                "date": "2023-12-31",
                "type": "R",
                "category": "gen",
                "amount": -12.0,
                "description": "test-1",
            },
        ]

        for r, e in zip(response.json(), expected):
            assert approx_dict(r, e)


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

        assert response.status_code == 200
        assert len(response.json()) == 2

        expected = [
            {
                "id": 3,
                "date": "2023-12-04",
                "type": "M",
                "category": "trial",
                "amount": -13.5,
                "description": "test-2.5",
            },
            {
                "id": 2,
                "date": "2023-12-15",
                "type": "C",
                "category": "test",
                "amount": -13.0,
                "description": "test-2",
            },
        ]

        for r, e in zip(response.json(), expected):
            assert approx_dict(r, e)


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

        assert response.status_code == 200
        assert len(response.json()) == 1

        expected = [
            {
                "id": 3,
                "date": "2023-12-04",
                "type": "M",
                "category": "trial",
                "amount": -13.5,
                "description": "test-2.5",
            },
        ]

        for r, e in zip(response.json(), expected):
            assert approx_dict(r, e)


def test_add_api(test_client):
    """Tests adding function."""
    with CRUDHandlerTestContext():
        # Skipping category
        response = test_client.post(
            "/add",
            json={
                "date": "2023-12-12",
                "type": "M",
                "amount": -1.44,
                "description": "added via API",
            },
        )
        assert response.status_code == 200
        assert response.json() == {"message": "expense added"}

        assert test_client.get("/query?types=M").json() == [
            {
                "id": 3,
                "date": "2023-12-04",
                "type": "M",
                "category": "trial",
                "amount": -13.5,
                "description": "test-2.5",
            },
            {
                "id": 6,
                "date": "2023-12-12",
                "type": "M",
                "category": "",
                "amount": -1.44,
                "description": "added via API",
            },
        ]


def test_load_api(test_client):
    """Tests loading function."""

    with CRUDHandlerTestContext() as ch:
        # fmt: off
        response = test_client.post(
            "/load"
            "?csvfile=resources/test-1.csv"
        )
        # fmt: on
        assert response.status_code == 200
        assert response.json() == {"message": "file loaded"}

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
            "/update/?id=3",
            json = {
                "date": "2028-05-01",
            },
        )
        assert response.status_code == 200
        assert response.json() == {"message": "expense updated"}

        response = test_client.patch(
            "/update/?id=1",
            json = {
                "type": "P",
                "amount": +10.00,
            },
        )
        assert response.status_code == 200
        assert response.json() == {"message": "expense updated"}

        response = test_client.get("/query")

        expected = [
            {
                "id": 5,
                "date": "2023-11-15",
                "type": "K",
                "category": "more",
                "amount": -15.0,
                "description": "test-4",
            },
            {
                "id": 4,
                "date": "2023-12-01",
                "type": "T",
                "category": "test",
                "amount": -14.0,
                "description": "test-3",
            },
            {
                "id": 2,
                "date": "2023-12-15",
                "type": "C",
                "category": "test",
                "amount": -13.0,
                "description": "test-2",
            },
            {
                "id": 1,
                "date": "2023-12-31",
                "type": "P",
                "category": "gen",
                "amount": +10.0,
                "description": "test-1",
            },
            {
                "id": 3,
                "date": "2028-05-01",
                "type": "M",
                "category": "trial",
                "amount": -13.5,
                "description": "test-2.5",
            },
        ]

        for r, e in zip(response.json(), expected):
            assert approx_dict(r, e)

        # Inexistent ID
        response = test_client.patch(
            "/update/?id=19",
            json = {
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
            {
                "id": 5,
                "date": "2023-11-15",
                "type": "K",
                "category": "more",
                "amount": -15.0,
                "description": "test-4",
            },
            {
                "id": 4,
                "date": "2023-12-01",
                "type": "T",
                "category": "test",
                "amount": -14.0,
                "description": "test-3",
            },
            {
                "id": 2,
                "date": "2023-12-15",
                "type": "C",
                "category": "test",
                "amount": -13.0,
                "description": "test-2",
            },
        ]

        for r, e in zip(response.json(), expected):
            assert approx_dict(r, e)

        # Inexistent ID
        response = test_client.delete("/remove/?ids=19")
        assert response.status_code == 404
        assert response.json() == {"detail": "ID 19 not found"}

        # Complete removal
        response = test_client.delete("/remove")

        assert response.status_code == 200
        assert response.json() == {"message": "expense(s) removed"}

        response = test_client.get("/query")
        assert not response.json()
