# pylint: disable=missing-function-docstring

"""API definitions.

Functions
-----------------------
get_ch()
    Yield CRUDHandler object for DB connection.

@app.get("/")
    Connect to the main page.
@app.post("/add")
    Add expense to the DB.
@app.get("/query")
    Return expenses matching specified filters.
@app.get("/summarize")
    Summarize expenses matching specified filters.
@app.post("/load")
    Append content of CSV file to DB.
@app.get("/save")
    Save current content of DB to CSV file.
@app.patch("/update")
    Update existing expense selected by ID.
@app.delete("/remove")
    Remove selected expenses.
@app.delete("/erase")
    Remove all expenses.
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


from typing import List
from typing import Dict
from typing import Annotated
from typing import Optional

from fastapi import FastAPI
from fastapi import Depends
from fastapi import Query
from fastapi import Body
from fastapi import HTTPException

from modules.schemas import ExpenseAdd
from modules.schemas import ExpenseRead
from modules.schemas import ExpenseUpdate
from modules.schemas import QueryParameters
from modules.crud_handler import CRUDHandlerError
from modules.crud_handler import CRUDHandler


app = FastAPI(title="sem")


def get_ch() -> CRUDHandler:
    """Yield CRUDHandler object for DB connection.

    Yields
    -----------------------
    CRUDHandler
        The CRUDHandler object.
    """
    ch = CRUDHandler()
    try:
        yield ch
    finally:
        ch.close()


@app.get(
    "/",
    status_code=200,
    description="Connect to the main page.",
    responses={
        200: {
            "model": Dict,
            "description": "Homepage reached.",
            "content": {
                "application/json": {
                    "example": {"message": "homepage reached"}
                }
            },
        }
    },
)
def root():
    return {"message": "homepage reached"}


@app.post(
    "/add",
    status_code=200,
    description="Add expense to the DB.",
    responses={
        200: {
            "model": Dict,
            "description": "Expense added.",
            "content": {"application/json": {"message": "expense added"}},
        },
    },
)
def add(
    data: Annotated[ExpenseAdd, Body(description="Expense to add.")],
    ch: CRUDHandler = Depends(get_ch),
):
    ch.add(data)
    return {"message": "expense added"}


@app.get(
    "/query",
    status_code=200,
    description="Return expenses matching specified filters.",
    responses={
        200: {
            "model": List[ExpenseRead],
            "description": "List of matching expenses.",
        },
    },
)
def query(
    start: Annotated[
        Optional[str],
        Query(
            description="Start date (included). `None` returns all expenses.",
        ),
    ] = None,
    end: Annotated[
        Optional[str],
        Query(
            description="End date (included). `None` returns all expenses.",
        ),
    ] = None,
    types: Annotated[
        Optional[List[str]],
        Query(
            description="Included expense types. `None` does not filter.",
        ),
    ] = None,
    categories: Annotated[
        Optional[List[str]],
        Query(
            description="Included expense categories. `None` does not filter.",
        ),
    ] = None,
    ch: CRUDHandler = Depends(get_ch),
):
    # Strong typing in the API description ignores list parameters,
    # fix requires re-definition of model here
    return ch.query(
        QueryParameters(
            start=start, end=end, types=types, categories=categories
        )
    )


@app.get(
    "/summarize",
    status_code=200,
    description="Summarize expenses matching specified filters.",
    responses={
        200: {
            "model": Dict[str, Dict[str, float]],
            "description": "Amount sums, grouped by category and type.",
        },
    },
)
def summarize(
    start: Annotated[
        Optional[str],
        Query(
            description="""Start date (included). Not filtered on if `None`
            (default)."""
        ),
    ] = None,
    end: Annotated[
        Optional[str],
        Query(
            description="""End date (included). Not filtered on if `None`
            (default)."""
        ),
    ] = None,
    types: Annotated[
        Optional[List[str]],
        Query(
            description="""Included expense types. Not filtered on if `None`
            (default)."""
        ),
    ] = None,
    categories: Annotated[
        Optional[List[str]],
        Query(
            description="""Included expense categories. Not filtered on if
            `None` (default)."""
        ),
    ] = None,
    ch: CRUDHandler = Depends(get_ch),
):
    # Strong typing in the API description ignores list parameters,
    # fix requires re-definition of model here
    return ch.summarize(
        QueryParameters(
            start=start, end=end, types=types, categories=categories
        )
    )


@app.post(
    "/load",
    status_code=200,
    description="Append content of CSV file to DB.",
    responses={
        200: {
            "model": Dict,
            "description": "CSV content loaded.",
            "content": {"application/json": {"message": "file loaded"}},
        },
        404: {
            "model": Dict,
            "description": "CSV file not found.",
            "content": {"application/json": {"detail": "<file> not found"}},
        },
        422: {
            "model": Dict,
            "description": "Invalid row or field.",
            "content": {
                "application/json": {
                    "detail": "<file> :: row <row> :: <error>"
                }
            },
        },
    },
)
def load(
    csvfile: Annotated[str, Query(description="Path to the CSV file.")],
    ch: CRUDHandler = Depends(get_ch),
):
    try:
        ch.load(csvfile)
    except FileNotFoundError as err:
        raise HTTPException(status_code=404, detail=str(err)) from err
    except CRUDHandlerError as err:
        raise HTTPException(status_code=422, detail=str(err)) from err

    return {"message": "file loaded"}


@app.get(
    "/save",
    status_code=200,
    description="Save current content of DB to CSV file.",
    responses={
        200: {
            "model": Dict,
            "description": "CSV content saved.",
            "content": {"application/json": {"message": "file saved"}},
        },
    },
)
def save(
    csvfile: Annotated[str, Query(description="Path to the CSV file.")],
    ch: CRUDHandler = Depends(get_ch),
):
    ch.save(csvfile)
    return {"message": "file saved"}


@app.patch(
    "/update",
    status_code=200,
    description="Update existing expense selected by ID.",
    responses={
        200: {
            "model": Dict,
            "description": "Expense updated.",
            "content": {"application/json": {"message": "expense updated"}},
        },
        404: {
            "model": Dict,
            "description": "Expense ID not found.",
            "content": {"application/json": {"detail": "ID <id> not found"}},
        },
    },
)
def update(
    ID: Annotated[int, Query(description="ID of the expense to update.")],
    data: Annotated[ExpenseUpdate, Body(description="New expense fields.")],
    ch: CRUDHandler = Depends(get_ch),
):
    try:
        ch.update(ID, data)
    except CRUDHandlerError as err:
        raise HTTPException(status_code=404, detail=str(err)) from err
    return {"message": "expense updated"}


@app.delete(
    "/remove",
    status_code=200,
    description="Remove selected expenses.",
    responses={
        200: {
            "model": Dict,
            "description": "Expense(s) removed.",
            "content": {"application/json": {"message": "expense(s) removed"}},
        },
        404: {
            "model": Dict,
            "description": "Expense ID not found.",
            "content": {"application/json": {"detail": "ID <id> not found"}},
        },
    },
)
def remove(
    ids: Annotated[
        List[int],
        Query(description="IDs of the expense(s) to remove."),
    ],
    ch: CRUDHandler = Depends(get_ch),
):
    try:
        ch.remove(ids)
    except CRUDHandlerError as err:
        raise HTTPException(status_code=404, detail=str(err)) from err
    return {"message": "expense(s) removed"}


@app.delete(
    "/erase",
    status_code=200,
    description="Remove all expenses.",
    responses={
        200: {
            "model": Dict,
            "description": "Database erased.",
            "content": {"application/json": {"message": "database erased"}},
        },
    },
)
def erase(ch: CRUDHandler = Depends(get_ch)):
    ch.erase()
    return {"message": "database erased"}
