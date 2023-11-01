# pylint: disable=missing-function-docstring

"""API definitions.

Functions
-----------------------
get_ch()
    Yield CRUDHandler object for DB connection.

@app.get("/")
    Connect to the main page.
@app.post("/access/{database}")
    Create new or connect to existing DB.
@app.post("/add")
    Add expense to the DB.
@app.get("/query")
    Return expenses within time window.
"""

# Copyright (c) 2023 Adriano Angelone
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# This file is part of sem-cli.
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

from fastapi import FastAPI
from fastapi import Depends
from fastapi import Path

from modules.schemas import ExpenseAdd
from modules.schemas import ExpenseRead
from modules.crud_handler import QueryParameters
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
                "application/json": {"example": {"message": "homepage reached"}}
            },
        }
    },
)
def root():
    return {"message": "homepage reached"}


@app.post(
    "/access/{database:path}",
    status_code=200,
    description="Create new or connect to existing DB.",
    responses={
        200: {
            "model": Dict,
            "description": "DB successfully created.",
            "content": {
                "application/json": {
                    "example": {"message": "DB created/accessed"}
                }
            },
        },
    },
)
def access_database(
    database: Annotated[str, Path(description="The DB to create/access.")],
    ch: CRUDHandler = Depends(get_ch),
):
    ch.connect(database)
    return {"message": "DB created/accessed"}


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
def add(data: ExpenseAdd, ch: CRUDHandler = Depends(get_ch)):
    ch.add(data)
    return {"message": "expense added"}


@app.get(
    "/query",
    status_code=200,
    description="Return expenses within time window.",
    responses={
        200: {
            "model": List[ExpenseRead],
            "description": "List of matching expenses.",
        },
    },
)
def query(
    params: QueryParameters = Depends(),
    ch: CRUDHandler = Depends(get_ch)
):
    return ch.query(params)
