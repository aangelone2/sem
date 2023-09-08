"""
Entrypoint, prompts the user for data and requests CRUD operations.

Functions
-----------------------
"""


from rich.console import Console

from modules.database import init_session
from modules.crud import query


console = Console()
session = init_session("test.sqlite")


def request_query():
    """Request query to CRUD interface, user input prompted."""
    console.print("[bold green]Requested query[/bold green]")

    start = console.input(
        "    [cyan]Starting date (included) :: [/cyan]"
    )
    end = console.input(
        "    [cyan]Ending date (included)   :: [/cyan]"
    )

    print(query(session, start, end))


#    console.rule("[bold cyan]Requested query")


request_query()
