from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from db.models import Base


def init_db(db_path: str) -> sessionmaker[Session]:
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)
