import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///reco.db")

# For SQLite relative path, ensure proper URL format
if DATABASE_URL.startswith("sqlite://") and not DATABASE_URL.startswith("sqlite:///"):
    # normalize e.g. sqlite://reco.db -> sqlite:///reco.db
    DATABASE_URL = DATABASE_URL.replace("sqlite://", "sqlite:///")

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

def init_db():
    from models import Ticket, Product, RnDRecord, TrialRecord, ComplaintRecord
    Base.metadata.create_all(bind=engine)
