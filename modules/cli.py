"""CLI functions to perform server requests.

Functions
-----------------------
root()
    Connect to the main page.
add()
    Add an Expense, querying the user for data.
query()
    Query the DB for expenses matching filters.
summarize()
    Query the DB for expenses matching filters.
load()
    Append the contents of a CSV file to the database.
save()
    Save the contents of the database to a CSV file.
update()
    Update an existing expense, selected by ID.
remove()
    Remove expenses selected by ID.
erase()
    Remove all expenses and reset ID field.
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


import os

from fastapi.encoders import jsonable_encoder

import requests

# `rich` works for tables and general printing
from rich.console import Console
from rich.table import Table

# `colorama` works for input() in docker
from colorama import Fore
from colorama import Style

from modules.schemas import ExpenseAdd
from modules.schemas import ExpenseUpdate


console = Console()
# Emphasis formatting - rich
em = "[bold green]"
# Emphasis formatting - colorama
EM = Fore.GREEN + Style.BRIGHT
NEM = Style.RESET_ALL

if os.environ.get("SEM_DOCKER") == "1":
    server = "http://sem-server:8000"
else:
    server = "http://127.0.0.1:8000"


def root():
    """Connect to the main page."""
    response = requests.get(server + "/")

    console.print(response.status_code)
    console.print(response.json())


def add():
    """Add an Expense, querying the user for data."""
    date = input(f"{EM}Date{NEM} (YYYY-MM-DD)   :: ")
    typ = input(f"{EM}Type{NEM}                :: ")
    category = input(f"{EM}Category{NEM} (optional) :: ")
    amount = input(f"{EM}Amount{NEM}              :: ")
    description = input(f"{EM}Description{NEM}         :: ")

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

    console.print(response.status_code)
    console.print(response.json())


def _get_query_parameters() -> str:
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
    start = input(f"{EM}Start date{NEM} (YYYY-MM-DD, optional)      :: ")
    start = f"&start={start}" if start else ""

    end = input(f"{EM}End date{NEM} (YYYY-MM-DD, optional)        :: ")
    end = f"&end={end}" if end else ""

    types = input(f"{EM}Types{NEM} (comma-separated, optional)      :: ")
    if types:
        types = types.split(",")
        types = "".join([f"&types={t}" for t in types])

    cat = input(f"{EM}Categories{NEM} (comma-separated, optional) :: ")
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
    qparams = _get_query_parameters()
    response = requests.get(server + "/query/" + qparams)

    console.print(response.status_code)

    table = Table()
    table.add_column(f"{em}ID[/]")
    table.add_column(f"{em}Date[/]")
    table.add_column(f"{em}Type[/]")
    table.add_column(f"{em}Category[/]")
    table.add_column(f"{em}Amount[/]")
    table.add_column(f"{em}Description[/]")

    # List of expenses (as dictionaries)
    for exp in response.json():
        table.add_row(
            str(exp["id"]),
            exp["date"],
            exp["type"],
            exp["category"],
            str(exp["amount"]),
            exp["description"],
        )

    console.print(table)


def summarize():
    """Query the DB for expenses matching filters.

    Obtains query parameters from the user.
    """
    qparams = _get_query_parameters()
    response = requests.get(server + "/summarize/" + qparams)

    console.print(response.status_code)

    # Dictionary of dictionaries (categories -> types -> sums)
    for cat in response.json():
        console.print(f"{em}Category[/] :: {cat}")

        table = Table()
        table.add_column(f"{em}Type[/]")
        table.add_column(f"{em}Total[/]")

        for tp in response.json()[cat]:
            table.add_row(tp, str(response.json()[cat][tp]))

        console.print(table)
        console.print("")


def load(csvfile: str):
    """Append the contents of a CSV file to the database.

    Parameters
    -----------------------
    csvfile : str
        Path of the CSV file.
    """
    response = requests.post(server + "/load/?csvfile=" + csvfile)

    console.print(response.status_code)
    console.print(response.json())


def save(csvfile: str):
    """Save the contents of the database to a CSV file.

    Parameters
    -----------------------
    csvfile : str
        Path of the CSV file.
    """
    response = requests.get(server + "/save/?csvfile=" + csvfile)

    console.print(response.status_code)
    console.print(response.json())


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

    console.print(response.status_code)
    console.print(response.json())


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

    console.print(response.status_code)
    console.print(response.json())


def erase():
    """Remove all expenses and reset ID field."""
    response = requests.delete(server + "/erase")

    console.print(response.status_code)
    console.print(response.json())
