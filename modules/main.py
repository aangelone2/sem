"""
Entrypoint, console interfaces to CRUD functions.

Functions
-----------------------
create_db()
    Create/overwrite DB with appropriate schema.
request_query()
    Request query + summary to CRUD interface.
request_load()
    Request load CRUD interface.
request_add()
    Add expense(s) to the DB.

main()
    Implement main entrypoint.
"""

# Copyright (c) 2023 Adriano Angelone
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the
# Software.
#
# This file is part of sem-cli.
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
from modules.schemas import ExpenseAdd
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
    """Request query + summary to CRUD interface.

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
    start = str2date(start) if start != "" else None

    # Skipping 2nd date if skipped 1st
    if start is not None:
        end = console.input(
            "[cyan]Ending date (included)   :: [/cyan]"
        )
        end = str2date(end) if end != "" else None
    else:
        end = None

    console.print("")

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

    console.print("")

    res = ch.summarize(start, end)

    table = Table()
    table.add_column("Type")
    table.add_column("Amount")

    for record in res:
        table.add_row(str(record[0]), str(record[1]))

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


def request_add(path: str):
    """Add expense(s) to the DB.

    Parameters
    -----------------------
    path : str
        DB path
    """
    ch = CRUDHandler(path, new=False)

    console.rule(
        f"[bold green]Adding expenses at {path}[/bold green]"
    )

    date = ""
    typ = ""
    amount = ""
    justification = ""

    while True:
        date = console.input("[cyan]Date          :: [/cyan]")

        typ = console.input("[cyan]Type          :: [/cyan]")

        amount = console.input(
            "[cyan]Amount        :: [/cyan]"
        )

        justification = console.input(
            "[cyan]Justification :: [/cyan]"
        )

        ch.add(
            ExpenseAdd(
                date=date,
                type=typ,
                amount=amount,
                justification=justification,
            )
        )

        console.print("")


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

    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("path", type=str)

    args = parser.parse_args()

    if args.command == "create":
        create_db(args.path)
    elif args.command == "query":
        request_query(args.path)
    elif args.command == "load":
        request_load(args.path, args.load)
    elif args.command == "add":
        request_add(args.path)


if __name__ == "__main__":
    main()
