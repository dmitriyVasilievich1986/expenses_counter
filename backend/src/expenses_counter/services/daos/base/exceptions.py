"""Custom exceptions for Data Access Object (DAO) operations.

This module defines application-specific exceptions used throughout the DAO layer
to handle various database operation errors. These exceptions provide a consistent
error handling interface and help distinguish between different types of database failures.

Classes:
    DBException: Base exception for all database-related errors.
    NotFoundException: Raised when a requested database record is not found.
    RelationshipNotFoundException: Raised when a foreign key constraint is violated.
"""

__all__ = ("DBException", "NotFoundException", "RelationshipNotFoundException")


class DBException(BaseException):
    """Base exception for database-related errors.

    This is the parent exception class for all database operations. It can be used
    to catch any database-related error in a generic way, or be raised directly
    for general database errors that don't fit into more specific categories.

    Inherits from BaseException to distinguish database errors from standard
    application exceptions.
    """

    pass


class NotFoundException(DBException):
    """Exception raised when a database record is not found.

    This exception is typically raised when:
    - A query for a specific record by ID returns no results
    - A SQLAlchemy NoResultFound exception is caught

    Attributes:
        message: A descriptive error message indicating the entity was not found.

    """

    message: str = "Entity not found"


class RelationshipNotFoundException(DBException):
    """Exception raised when a foreign key constraint is violated.

    This exception is typically raised when:
    - Attempting to create/update a record with an invalid foreign key
    - SQLAlchemy IntegrityError is caught during database operations
    - A required relationship between entities cannot be established

    Attributes:
        message: A descriptive error message indicating the relationship issue.

    """

    message: str = "Relationship not found"
