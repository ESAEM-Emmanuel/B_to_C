from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import sessionmaker
from app import config_sething

# DATABASE_URL = f"'postgresql'://'postgres':'admin'@'localhost':5432/'polo_db'"
# DATABASE_URL = "postgresql://postgres:admin@localhost:5432/polo_db"
DATABASE_URL = f"{config_sething.database_client}://{config_sething.database_username}:{config_sething.database_password}@{config_sething.database_hostname}:{config_sething.database_port}/{config_sething.database_name}"
engine = create_engine(DATABASE_URL)
Base = declarative_base()
# Base: DeclarativeMeta = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Database Dependencies
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
