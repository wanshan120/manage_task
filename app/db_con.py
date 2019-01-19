import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager

"""SQLAlchemyの初期設定をする."""

Base = declarative_base()
test = 'mysql+pymysql://root:Fzsiguca5@@localhost/test_sa_test?charset=utf8'
pro = 'mysql+pymysql://root:Fzsiguca5@@localhost/sa_test_db?charset=utf8'


@contextmanager
def session_scope(url):
    """Provide a transactional scope around a series of operations."""
    engine = sa.create_engine(url)  # , echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        import traceback
        traceback.print_exc()
        raise
    finally:
        session.close()
