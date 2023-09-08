"""Common utility functions.

Functions
-----------------------
str2date():
    Convert string in YYYY-MM-DD format to date.
"""


from datetime import datetime


def str2date(arg: str) -> datetime.date:
    """Convert string in YYYY-MM-DD format to date.

    Parameters
    -----------------------
    arg : str
        The string to convert

    Returns
    -----------------------
    datetime.date
        The converted datetime
    """
    return datetime.strptime(arg, "%Y-%m-%d").date()
