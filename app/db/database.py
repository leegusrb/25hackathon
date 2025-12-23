from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 프로젝트 폴더에 'hackathon.db'라는 파일이 생깁니다.
SQLALCHEMY_DATABASE_URL = "sqlite:///./hackathon.db"

# SQLite는 쓰레드 통신에 대한 체크를 꺼야 합니다 (check_same_thread=False)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency (API에서 DB 세션을 쓰고 닫게 해주는 함수)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()