from asyncio import current_task

from sqlalchemy.ext.asyncio import (
    create_async_engine, async_sessionmaker,
    async_scoped_session)

from core.config import settings


class DatabaseHandler:
    def __init__(self, url: str = settings.postgres_async_db_url, echo: bool = settings.db_echo):
        """
        Initialize the database handler with the given URL and echo setting.

        :param url: The URL of the database to connect to. Defaults to the value of the
            `postgres_async_db_url` setting.
        :param echo: Whether to enable echo mode for the database connection. Defaults to the
            value of the `db_echo` setting.
        """
        self.engine = create_async_engine(url=url, echo=echo)
        self.async_session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    def get_scoped_session(self):
        """
        Get a scoped session factory that uses the current task as the scope.

        The returned session factory will create a new session for each task that
        is created. The session will be closed when the task is finished.

        :return: A scoped session factory that uses the current task as the scope.
        :rtype: Callable[[], AsyncSession]
        """
        session = async_scoped_session(
            session_factory=self.async_session_factory,
            scopefunc=current_task,
        )
        return session

    async def session_dependency(self):
        """
        A dependency that yields a database session and closes it when finished.

        This dependency is a context manager that yields a database session when
        entered, and closes the session when exited. This ensures that the session
        is always properly closed, even if an exception is raised.

        :yield: The database session to use.
        :rtype: AsyncSession
        """
        async with self.async_session_factory() as session:
            yield session

    async def scoped_session_dependency(self):
        """
        A dependency that yields a database session and removes it when finished.

        This dependency is a context manager that yields a database session when
        entered, and removes the session when exited. This ensures that the session
        is always properly removed, even if an exception is raised.

        :yield: The database session to use.
        :rtype: AsyncSession
        """
        session = self.get_scoped_session()
        try:
            yield session
        finally:
            session.remove()


db_handler = DatabaseHandler()
