from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_URL = "sqlite:///./realworldapp.db"
connect_args = {"check_same_thread": False}

engine = create_engine(DB_URL, connect_args=connect_args)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
