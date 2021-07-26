from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from os import environ

# host=environ.get('HOST', 'concildevblackbox.c0rzxyeauhjq.us-east-1.rds.amazonaws.com')
# database=environ.get('DATABASE', 'concildevblackboxdatabase')
# user=environ.get('USER', 'awsuser')
# password=environ.get('PASSWORD', 'Ox!g3n!0')
# port=environ.get('PORT', 5432)

# SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
SQLALCHEMY_DATABASE_URL = "sqlite:///./gmstore.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)
Base = declarative_base()