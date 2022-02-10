from dataclasses import dataclass

from sqlalchemy import Column, Date, Integer, MetaData, String, Table
from sqlalchemy.engine.mock import MockConnection

from app.core import DbAddUserIn


@dataclass
class UserRepository:
    USERS_TABLE_NAME = "users"

    def get_table(self, metadata: MetaData) -> Table:
        return Table(
            self.USERS_TABLE_NAME,
            metadata,
            Column("id", Integer, primary_key=True, nullable=False, autoincrement=True),
            Column("api_key", String, nullable=False),
            Column("name", String, nullable=False),
            Column("create_date_utc", Date, nullable=False),
        )

    def create_tables(self, engine: MockConnection) -> None:
        if not engine.dialect.has_table(engine.connect(), self.USERS_TABLE_NAME):
            metadata = MetaData(engine)
            self.get_table(metadata)
            metadata.create_all(engine)

    def add_user(self, engine: MockConnection, user: DbAddUserIn) -> DbAddUserIn:
        metadata = MetaData(engine)
        users = self.get_table(metadata)
        ins = users.insert().values(
            api_key=user.api_key,
            name=user.name,
            create_date_utc=user.create_date_utc,
        )
        con = engine.connect()
        con.execute(ins)
        # TODO get execute response from that
        return user
