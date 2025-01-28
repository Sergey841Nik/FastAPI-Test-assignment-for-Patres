from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.config import settings


class DBHelper:
    def __init__(self, url: str, echo: bool = False):
        self.engine = create_async_engine(
            url=url,
            echo=echo,
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    async def despose(self):
        await self.engine.dispose()

    async def session_dependency(self):
        async with self.session_factory() as sessinon:
            yield sessinon
            


db_helper = DBHelper(
    url=settings.url,
    echo=settings.echo,
)
