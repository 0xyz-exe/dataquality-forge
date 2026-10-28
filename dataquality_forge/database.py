from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dataquality_forge.config import DATABASE_URL

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from dataquality_forge import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
