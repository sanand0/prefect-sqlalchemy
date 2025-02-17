# prefect-sqlalchemy

<p align="center">
    <img src="https://user-images.githubusercontent.com/15331990/217670791-ecce97ef-8f14-4519-85b7-40cd28ac2325.png">
    <br>
    <a href="https://pypi.python.org/pypi/prefect-sqlalchemy/" alt="PyPI version">
        <img alt="PyPI" src="https://img.shields.io/pypi/v/prefect-sqlalchemy?color=0052FF&labelColor=090422"></a>
    <a href="https://github.com/PrefectHQ/prefect-sqlalchemy/" alt="Stars">
        <img src="https://img.shields.io/github/stars/PrefectHQ/prefect-sqlalchemy?color=0052FF&labelColor=090422" /></a>
    <a href="https://pepy.tech/badge/prefect-sqlalchemy/" alt="Downloads">
        <img src="https://img.shields.io/pypi/dm/prefect-sqlalchemy?color=0052FF&labelColor=090422" /></a>
    <a href="https://github.com/PrefectHQ/prefect-sqlalchemy/pulse" alt="Activity">
        <img src="https://img.shields.io/github/commit-activity/m/PrefectHQ/prefect-sqlalchemy?color=0052FF&labelColor=090422" /></a>
    <br>
    <a href="https://prefect-community.slack.com" alt="Slack">
        <img src="https://img.shields.io/badge/slack-join_community-red.svg?color=0052FF&labelColor=090422&logo=slack" /></a>
    <a href="https://discourse.prefect.io/" alt="Discourse">
        <img src="https://img.shields.io/badge/discourse-browse_forum-red.svg?color=0052FF&labelColor=090422&logo=discourse" /></a>
</p>

Visit the full docs [here](https://PrefectHQ.github.io/prefect-sqlalchemy) to see additional examples and the API reference.

The prefect-sqlalchemy collection makes it easy to connect to a database in your Prefect flows. Check out the examples below to get started!

## Getting Started

### Integrate with Prefect flows

Prefect and SQLAlchemy are a data powerhouse duo. With Prefect, your data pipelines are always on track, and with SQLAlchemy, your databases are a snap to handle! Get ready to experience the ultimate data "flow-chemistry"!

To set up a table, use the `execute` and `execute_many` methods. Then, use the `fetch_many` method to retrieve data in a stream until there's no more data.

By using the `SqlAlchemyConnector` as a context manager, you can make sure that the SQLAlchemy engine and any connected resources are closed properly after you're done with them.

Be sure to install [prefect-sqlalchemy](#installation) and [save to block](#saving-credentials-to-block) to run the examples below!

!!! note "Async support"

    `SqlAlchemyConnector` also supports async workflows! Just be sure to save, load, and use an async driver.
    ```python
    from prefect_sqlalchemy import SqlAlchemyConnector, ConnectionComponents, AsyncDriver

    connector = SqlAlchemyConnector(
        connection_info=ConnectionComponents(
            driver=AsyncDriver.SQLITE_AIOSQLITE,
            database="DATABASE-PLACEHOLDER.db"
        )
    )

    connector.save("BLOCK_NAME-PLACEHOLDER")
    ```

=== "Sync"

    ```python
    from prefect import flow, task
    from prefect_sqlalchemy import SqlAlchemyConnector


    @task
    def setup_table(block_name: str) -> None:
        with SqlAlchemyConnector.load(block_name) as connector:
            connector.execute(
                "CREATE TABLE IF NOT EXISTS customers (name varchar, address varchar);"
            )
            connector.execute(
                "INSERT INTO customers (name, address) VALUES (:name, :address);",
                parameters={"name": "Marvin", "address": "Highway 42"},
            )
            connector.execute_many(
                "INSERT INTO customers (name, address) VALUES (:name, :address);",
                seq_of_parameters=[
                    {"name": "Ford", "address": "Highway 42"},
                    {"name": "Unknown", "address": "Highway 42"},
                ],
            )

    @task
    def fetch_data(block_name: str) -> list:
        all_rows = []
        with SqlAlchemyConnector.load(block_name) as connector:
            while True:
                # Repeated fetch* calls using the same operation will
                # skip re-executing and instead return the next set of results
                new_rows = connector.fetch_many("SELECT * FROM customers", size=2)
                if len(new_rows) == 0:
                    break
                all_rows.append(new_rows)
        return all_rows

    @flow
    def sqlalchemy_flow(block_name: str) -> list:
        setup_table(block_name)
        all_rows = fetch_data(block_name)
        return all_rows


    sqlalchemy_flow("BLOCK_NAME-PLACEHOLDER")
    ```

=== "Async"

    ```python
    from prefect import flow, task
    from prefect_sqlalchemy import SqlAlchemyConnector
    import asyncio

    @task
    async def setup_table(block_name: str) -> None:
        async with await SqlAlchemyConnector.load(block_name) as connector:
            await connector.execute(
                "CREATE TABLE IF NOT EXISTS customers (name varchar, address varchar);"
            )
            await connector.execute(
                "INSERT INTO customers (name, address) VALUES (:name, :address);",
                parameters={"name": "Marvin", "address": "Highway 42"},
            )
            await connector.execute_many(
                "INSERT INTO customers (name, address) VALUES (:name, :address);",
                seq_of_parameters=[
                    {"name": "Ford", "address": "Highway 42"},
                    {"name": "Unknown", "address": "Highway 42"},
                ],
            )

    @task
    async def fetch_data(block_name: str) -> list:
        all_rows = []
        async with SqlAlchemyConnector.load(block_name) as connector:
            while True:
                # Repeated fetch* calls using the same operation will
                # skip re-executing and instead return the next set of results
                new_rows = await connector.fetch_many("SELECT * FROM customers", size=2)
                if len(new_rows) == 0:
                    break
                all_rows.append(new_rows)
        return all_rows

    @flow
    async def sqlalchemy_flow(block_name: str) -> list:
        await setup_table(block_name)
        all_rows = await fetch_data(block_name)
        return all_rows


    asyncio.run(sqlalchemy_flow("BLOCK_NAME-PLACEHOLDER"))
    ```

## Resources

For more tips on how to use tasks and flows in a Collection, check out [Using Collections](https://orion-docs.prefect.io/collections/usage/)!

### Installation

Install `prefect-sqlalchemy` with `pip`:

```bash
pip install prefect-sqlalchemy
```

Requires an installation of Python 3.7+.

We recommend using a Python virtual environment manager such as pipenv, conda or virtualenv.

These tasks are designed to work with Prefect 2.0. For more information about how to use Prefect, please refer to the [Prefect documentation](https://orion-docs.prefect.io/).

### Saving Credentials to Block

To use the `load` method on Blocks, you must already have a block document [saved through code](https://orion-docs.prefect.io/concepts/blocks/#saving-blocks) or [saved through the UI](https://orion-docs.prefect.io/ui/blocks/).

Below is a walkthrough on saving block documents through code; simply create a short script, replacing the placeholders. 

```python
from prefect_sqlalchemy import SqlAlchemyConnector, ConnectionComponents, SyncDriver

connector = SqlAlchemyConnector(
    connection_info=ConnectionComponents(
        driver=SyncDriver.POSTGRESQL_PSYCOPG2,
        username="USERNAME-PLACEHOLDER",
        password="PASSWORD-PLACEHOLDER",
        host="localhost",
        port=5432,
        database="DATABASE-PLACEHOLDER",
    )
)

connector.save("BLOCK_NAME-PLACEHOLDER")
```

Congrats! You can now easily load the saved block, which holds your credentials:

```python
from prefect_sqlalchemy import SqlAlchemyConnector

SqlAlchemyConnector.load("BLOCK_NAME-PLACEHOLDER")
```

The required keywords depend on the desired `driver`. For example, sqlite only requires driver and database specified:

```python
from prefect_sqlalchemy import SqlAlchemyConnector, ConnectionComponents, SyncDriver

connector = SqlAlchemyConnector(
    connection_info=ConnectionComponents(
        driver=SyncDriver.SQLITE_PYSQLITE,
        database="DATABASE-PLACEHOLDER.db"
    )
)

connector.save("BLOCK_NAME-PLACEHOLDER")
```

!!! info "Registering blocks"

    Register blocks in this module to
    [view and edit them](https://orion-docs.prefect.io/ui/blocks/)
    on Prefect Cloud:

    ```bash
    prefect block register -m prefect_sqlalchemy
    ```

A list of available blocks in `prefect-sqlalchemy` and their setup instructions can be found [here](https://PrefectHQ.github.io/prefect-sqlalchemy/blocks_catalog).

### Feedback

If you encounter any bugs while using `prefect-sqlalchemy`, feel free to open an issue in the [prefect-sqlalchemy](https://github.com/PrefectHQ/prefect-sqlalchemy) repository.

If you have any questions or issues while using `prefect-sqlalchemy`, you can find help in either the [Prefect Discourse forum](https://discourse.prefect.io/) or the [Prefect Slack community](https://prefect.io/slack).

Feel free to star or watch [`prefect-sqlalchemy`](https://github.com/PrefectHQ/prefect-sqlalchemy) for updates too!

### Contributing

If you'd like to help contribute to fix an issue or add a feature to `prefect-sqlalchemy`, please [propose changes through a pull request from a fork of the repository](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork).

Here are the steps:

1. [Fork the repository](https://docs.github.com/en/get-started/quickstart/fork-a-repo#forking-a-repository)
2. [Clone the forked repository](https://docs.github.com/en/get-started/quickstart/fork-a-repo#cloning-your-forked-repository)
3. Install the repository and its dependencies:
```
pip install -e ".[dev]"
```
4. Make desired changes
5. Add tests
6. Insert an entry to [CHANGELOG.md](https://github.com/PrefectHQ/prefect-sqlalchemy/blob/main/CHANGELOG.md)
7. Install `pre-commit` to perform quality checks prior to commit:
```
pre-commit install
```
8. `git commit`, `git push`, and create a pull request
