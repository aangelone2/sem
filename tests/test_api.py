# pylint: disable=redefined-outer-name,unused-import,duplicate-code
# required to avoid trouble with fixture declaration

"""Test module for API."""

from typing import Dict

import pytest
from pytest import approx
from fastapi.testclient import TestClient

from modules.api import app

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
        response = test_client.get("/query/")

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


def test_date_query(test_client):
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


def test_date_type_query(test_client):
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


def test_date_type_cat_query(test_client):
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
