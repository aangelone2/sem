"""CLI functions to perform server requests.

Functions
-----------------------
root()
    Connect to the main page.
"""

# Copyright (c) 2023 Adriano Angelone
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# This file is part of sem.
#
# This file may be used under the terms of the GNU General Public License
# version 3.0 as published by the Free Software Foundation and appearing in the
# file LICENSE included in the packaging of this file. Please review the
# following information to ensure the GNU General Public License version 3.0
# requirements will be met:
# http://www.gnu.org/copyleft/gpl.html.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import functools
import pprint

from fastapi.encoders import jsonable_encoder

import requests

from modules.schemas import ExpenseAdd
from modules.schemas import ExpenseUpdate


server = "http://127.0.0.1:8000"
pprint = functools.partial(pprint.pprint, indent=1)


def root():
    """Connect to the main page."""
    response = requests.get(server + "/")

    pprint(response.status_code)
    pprint(response.json())


def add():
    """Add an Expense, querying the user for data."""
    date = input("Expense date (YYYY-MM-DD) :: ")
    typ = input("Expense type :: ")
    category = input("Expense category, skippable :: ")
    amount = input("Expense amount :: ")
    description = input("Expense description :: ")

    response = requests.post(
        server + "/add",
        json=jsonable_encoder(
            ExpenseAdd(
                date=date,
                type=typ,
                category=category,
                amount=amount,
                description=description,
            )
        ),
    )

    pprint(response.status_code)
    pprint(response.json())


def get_query_parameters() -> str:
    """Query the user for QueryParameters content and returns a query string.

    Parameters
    -----------------------
    params : QueryParameters
        Input data object.

    Returns
    -----------------------
    str
        The prepared query parameter string.
    """
    start = input("Query start date (YYYY-MM-DD), skippable :: ")
    start = f"start={start}" if start else ""

    end = input("Query end date (YYYY-MM-DD), skippable :: ")
    end = f"end={end}" if end else ""

    types = input("Comma-separated expense types, skippable :: ")
    if types:
        types = types.split(",")
        types = "".join([f"&types={t}" for t in types])

    cat = input("Comma-separated expense categories, skippable :: ")
    if cat:
        cat = cat.split(",")
        cat = "".join([f"&cat={t}" for t in cat])

    url_params = start + end + types + cat
    # Remove possible starting &
    if url_params:
        if url_params[0] == "&":
            url_params = url_params[1:]

    return "?" + url_params


def query():
    """Query the DB for expenses matching filters.

    Obtains query parameters from the user.
    """
    qparams = get_query_parameters()
    print(qparams)
    response = requests.get(server + "/query/" + qparams)

    pprint(response.status_code)
    pprint(response.json())


def summarize():
    """Query the DB for expenses matching filters.

    Obtains query parameters from the user.
    """
    qparams = get_query_parameters()
    response = requests.get(server + "/summarize/" + qparams)

    pprint(response.status_code)
    pprint(response.json())


def load(csvfile: str):
    """Append the contents of a CSV file to the database.

    Parameters
    -----------------------
    csvfile : str
        Path of the CSV file.
    """
    response = requests.post(server + "/load/?csvfile=" + csvfile)

    pprint(response.status_code)
    pprint(response.json())


def save(csvfile: str):
    """Save the contents of the database to a CSV file.

    Parameters
    -----------------------
    csvfile : str
        Path of the CSV file.
    """
    response = requests.get(server + "/save/?csvfile=" + csvfile)

    pprint(response.status_code)
    pprint(response.json())


def update(ID: int, data: ExpenseUpdate):
    """Update an existing expense, selected by ID.

    Parameters
    -----------------------
    ID: int
        ID of the expense to update.
    data: ExpenseUpdate
        Object containing the new expense fields.
    """
    response = requests.patch(
        server + f"/update/?ID={ID}", json=jsonable_encoder(data)
    )

    pprint(response.status_code)
    pprint(response.json())


def remove(IDs: list[int]):
    """Remove expenses selected by ID.

    Parameters
    -----------------------
    ID: list[int]
        IDs of the expenses to remove.
    """
    id_str = "".join([f"&ids={i}" for i in IDs])
    id_str = id_str[1:]

    response = requests.delete(server + f"/remove/?{id_str}")

    pprint(response.status_code)
    pprint(response.json())


def erase():
    """Remove all expenses."""
    response = requests.delete(server + "/erase")

    pprint(response.status_code)
    pprint(response.json())
