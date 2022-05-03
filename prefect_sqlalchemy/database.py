from typing import TYPE_CHECKING, Union, Tuple, Any, Dict, Optional, List

from prefect import task
from sqlalchemy.sql import text

if TYPE_CHECKING:
    from prefect_sqlalchemy.credentials import SQLAlchemyCredentials
    from sqlalchemy.engine.cursor import CursorResult


async def _execute(
    query: str,
    sqlalchemy_credentials: "SQLAlchemyCredentials",
    params: Optional[Union[Tuple[Any], Dict[str, Any]]] = None,
) -> "CursorResult":
    """
    Executes a SQL query.
    """
    async with sqlalchemy_credentials.get_connection() as connection:
        result = await connection.execute(text(query), params)
        await connection.commit()
    return result


@task
async def sqlalchemy_execute(
    query: str,
    sqlalchemy_credentials: "SQLAlchemyCredentials",
    params: Optional[Union[Tuple[Any], Dict[str, Any]]] = None,
):
    """
    Executes a SQL query; useful for creating tables and inserting rows
    since this task does not return any objects.

    Args:
        query: The query to execute against the database.
        sqlalchemy_credentials: The credentials to use to authenticate.
        params: The params to replace the placeholders in the query.
    
    Examples:
        Create table named customers and insert values.
        ```python
        from prefect_sqlalchemy import SQLAlchemyCredentials
        from prefect_sqlalchemy.database import sqlalchemy_execute
        from prefect import flow

        @flow
        def sqlalchemy_execute_flow():
            sqlalchemy_credentials = SQLAlchemyCredentials(
                driver="postgresql",
                user="prefect",
                password="prefect_password",
                database="postgres",
            )
            sqlalchemy_execute(
                "CREATE TABLE IF NOT EXISTS customers (name varchar, address varchar);",
                sqlalchemy_credentials,
            )
            sqlalchemy_execute(
                "INSERT INTO customers (name, address) VALUES (:name, :address);",
                sqlalchemy_credentials,
                params={"name": "Marvin", "address": "Highway 42"}
            )

        sqlalchemy_execute_flow()
        ```
    """
    # do not return anything or else results in the error:
    # This result object does not return rows. It has been closed automatically
    await _execute(query, sqlalchemy_credentials, params=params)


@task
async def sqlalchemy_query(
    query: str,
    sqlalchemy_credentials: "SQLAlchemyCredentials",
    params: Optional[Union[Tuple[Any], Dict[str, Any]]] = None,
    limit: Optional[int] = None,
) -> List[Tuple[Any]]:
    """
    Executes a SQL query; useful for querying data from existing tables.

    Args:
        query: The query to execute against the database.
        sqlalchemy_credentials: The credentials to use to authenticate.
        params: The params to replace the placeholders in the query.
        limit: The number of rows to fetch.

    Returns:
        The fetched results.
    
    Examples:
        Query postgres table with the ID value parameterized.
        ```python
        from prefect_sqlalchemy import SQLAlchemyCredentials
        from prefect_sqlalchemy.database import sqlalchemy_query
        from prefect import flow

        @flow
        def sqlalchemy_query_flow():
            sqlalchemy_credentials = SQLAlchemyCredentials(
                driver="postgresql",
                user="prefect",
                password="prefect_password",
                database="postgres",
            )

            return result

        sqlalchemy_query_flow()
        ```
    """
    result = await _execute(query, sqlalchemy_credentials, params=params)
    if limit is None:
        return result.fetchall()
    else:
        return result.fetchmany(limit)
