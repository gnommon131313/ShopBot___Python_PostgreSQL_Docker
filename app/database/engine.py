from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os


# engine = create_engine('sqlite:///test_sqlite.db')  # Скорее всего когда-нибудь понидобиться для теста
engine = create_engine(os.getenv("DATABASE_URL"))  
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)