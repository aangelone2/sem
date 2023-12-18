"""Session initializer.

Functions
-----------------------
init_session()
    Init connection to specified DB and write schema.
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


from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy_utils import database_exists
from sqlalchemy_utils import create_database

from modules.models import Base


def init_session(database: str) -> Session:
    """Init connection to specified DB and write schema.

    Parameters
    -----------------------
    database : str
        Database name to connect to.

    Returns
    -----------------------
    sqlalchemy.orm.Session
        The initialized Session.
    """
    DRIVER = "postgresql+psycopg"
    USER = "postgres"
    PASSWORD = ""
    HOST = "localhost"
    PORT = "5432"

    DB = f"{DRIVER}://{USER}:{PASSWORD}@{HOST}:{PORT}/{database}"
    if not database_exists(DB):
        create_database(DB)

    engine = create_engine(DB)
    # Building schema
    Base.metadata.create_all(engine)

    return Session(bind=engine)
