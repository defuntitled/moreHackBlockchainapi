import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec

SqlalchemyBase = dec.declarative_base()

_factory = None


def global_init(db_name: str):
    global _factory
    if _factory:
        return
    if not db_name or not db_name.strip():
        raise Exception("Database name could be not empty")
    connect_str = f'postgresql+psycopg2://admin:root@localhost:5432/{db_name}'
    print(f"connect to database by url:{connect_str}")
    engine = sa.create_engine(connect_str, echo=False)
    _factory = orm.sessionmaker(bind=engine)
    SqlalchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global _factory
    return _factory()