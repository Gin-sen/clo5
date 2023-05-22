from os import getenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

db_host = getenv("DB_HOST", "localhost")
db_port = getenv("DB_PORT", "5432")
db_user = getenv("DB_USER", "Bobby")
db_pass = getenv("DB_PASS", "BR")
db_name = getenv("DB_NAME", "hotel-db")

# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
SQLALCHEMY_DATABASE_URL = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
    # connect_args={"check_same_thread": False} is needed only for SQLite.
    # It's not needed for other databases.
    # SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
