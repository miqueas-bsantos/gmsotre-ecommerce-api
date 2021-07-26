from sqlalchemy import create_engine  
from sqlalchemy.orm import sessionmaker
import psycopg2


class PostgreSql:
    
    def __init__(self, user, password, host, port, database):
        self.connection = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
        # self.connection = f"redshift+psycopg2://{user}:{password}@{host}:{port}/{database}"
        self.engine = create_engine(self.connection, echo=False, pool_size=30, max_overflow=20)
        self.Session = sessionmaker(bind=self.engine)
        
    
    def create_session(self):
        return self.Session()