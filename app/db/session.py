# In this file, we set up the database session and initialize the database for the job scheduler application and define the base class for our ORM models.


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import Config

engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

Base = declarative_base()


def init_db():
    from app.models.job import Job
    from app.models.job_execution import JobExecution
    Base.metadata.create_all(bind=engine)


























# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, declarative_base
# from app.config import Config

# engine = create_engine(
#     Config.SQLALCHEMY_DATABASE_URI,
#     pool_pre_ping=True
# )

# SessionLocal = sessionmaker(
#     bind=engine,
#     autoflush=False,
#     autocommit=False
# )

# Base = declarative_base()


# def init_db():
#     # IMPORTANT: models import yahin hona chahiye
#     from app.models.job import Job
#     from app.models.job_execution import JobExecution

#     Base.metadata.create_all(bind=engine)


# print("🔌 DB URL USED BY WORKER:", Config.SQLALCHEMY_DATABASE_URI)
