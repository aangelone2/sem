"""Interface functions for server requests.

Functions
-----------------------
root()
    Connect to the main page.
"""


import functools
import pprint

import requests

from modules.schemas import ExpenseAdd


server = "http://127.0.0.1:8000"
pprint = functools.partial(pprint.pprint, indent=1)


def root():
    """Connect to the main page."""
    response = requests.get(server + "/")

    pprint(response.status_code)
    pprint(response.json())


def access(database: str):
    """Create new or connect to existing DB.

    Parameters
    -----------------------
    database : str
        Path to the new/existing DB.
    """
    response = requests.get(server + f"/access/{database}")

    pprint(response.status_code)
    pprint(response.json())


def add(data: ExpenseAdd):
    """Add a metadata document to a collection.

    Parameters
    -----------------------
    data : ExpenseAdd
        Data of the expense to add.
    """
    response = requests.post(
        server + "/add",
        json={"data": data.model_dump(exclude_unset=True)},
    )

    pprint(response.status_code)
    pprint(response.json())
