"""Generic database utilities.

Functions
-----------------------
init_session()
    Create a Session object linked to the given ID.
"""


from sqlalchemy import create_engine
from sqlalchemy.orm import Session


def init_session(path: str) -> Session:
    """Create a Session object linked to the given path.

    Parameters
    -----------------------
    path : str
        The path to the DB

    Returns
    -----------------------
    Session
        The initialized Session
    """
    engine_str = "sqlite:///"

    return Session(bind=create_engine(engine_str + path))
