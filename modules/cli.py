"""Interface functions for server requests.

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
