"""
Entrypoint, console interfaces to CRUD functions.

Functions
-----------------------
create_db()
    Create/overwrite DB with appropriate schema.
request_query()
    Request query to CRUD interface, prompts for dates.

main()
    Implement main entrypoint.
"""

# Copyright (c) 2023 Adriano Angelone
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the
# Software.
#
# This file is part of sem.
#
# This file may be used under the terms of the GNU General
# Public License version 3.0 as published by the Free Software
# Foundation and appearing in the file LICENSE included in the
# packaging of this file.  Please review the following
# information to ensure the GNU General Public License version
# 3.0 requirements will be met:
# http://www.gnu.org/copyleft/gpl.html.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import argparse
from rich.console import Console
from rich.table import Table

from modules.common import str2date
from modules.crud import CRUDHandler


console = Console()


def create_db(path: str):
    """Create/overwrite DB with appropriate schema.

    Parameters
    -----------------------
    path : str
        DB path
    """
    _ = CRUDHandler(path, new=True)
    console.rule(
        f"[bold green]Generated DB at {path}[/bold green]"
    )


def request_query(path: str):
    """Request query to CRUD interface, prompts for dates.

    Parameters
    -----------------------
    path : str
        DB path
    """
    ch = CRUDHandler(path, new=False)

    console.rule(
        f"[bold green]Requested query at {path}[/bold green]"
    )

    start = console.input(
        "[cyan]Starting date (included) :: [/cyan]"
    )
    start = str2date(start)

    end = console.input(
        "[cyan]Ending date (included)   :: [/cyan]"
    )
    end = str2date(end)

    print("")

    res = ch.query(start, end)

    table = Table()
    table.add_column("ID")
    table.add_column("Date")
    table.add_column("Type")
    table.add_column("Amount")
    table.add_column("Justification")

    for record in res:
        table.add_row(
            str(record.id),
            str(record.date),
            record.type,
            str(record.amount),
            record.justification,
        )

    console.print(table)


def request_load(path: str, csv_path: str):
    """Request load CRUD interface.

    Parameters
    -----------------------
    path : str
        DB path
    csv_path : str
        CSV file path
    """
    ch = CRUDHandler(path, new=False)

    console.rule(
        f"[bold green]Requested load from {csv_path}[/bold green]"
    )

    ch.load(csv_path)

    console.rule(
        f"[bold green]Loading completed in {path}[/bold green]"
    )


def main():
    """Implement main entrypoint."""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    create_parser = subparsers.add_parser("create")
    create_parser.add_argument("path", type=str)

    query_parser = subparsers.add_parser("query")
    query_parser.add_argument("path", type=str)

    load_parser = subparsers.add_parser("load")
    load_parser.add_argument("path", type=str)
    load_parser.add_argument("-l", "--load", type=str)

    args = parser.parse_args()

    if args.command == "create":
        create_db(args.path)
    elif args.command == "query":
        request_query(args.path)
    elif args.command == "load":
        request_load(args.path, args.load)


if __name__ == "__main__":
    main()
