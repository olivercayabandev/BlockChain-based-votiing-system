from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, DateTime, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()


class Voter(Base):
    __tablename__ = "voters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    resident_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=False)
    is_verified = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)
    id_photo = Column(LargeBinary, nullable=True)
    consent_given = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    party = Column(String(100), nullable=True)
    description = Column(String(500), nullable=True)
    image_url = Column(String(200), nullable=True)


class VoteTransaction(Base):
    __tablename__ = "vote_transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    resident_id = Column(String(50), nullable=False)
    candidate_id = Column(String(50), nullable=False)
    transaction_hash = Column(String(100), unique=True, nullable=False)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    block_index = Column(Integer, nullable=True)


class OTP(Base):
    __tablename__ = "otps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    phone_number = Column(String(20), nullable=False)
    otp_code = Column(String(6), nullable=False)
    resident_id = Column(String(50), nullable=True)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


DATABASE_URL = "sqlite:///voting.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_candidates(db):
    existing = db.query(Candidate).first()
    if existing:
        return

    candidates = [
        Candidate(candidate_id="PILIPINAS", name="Maria Santos", party="Party List", description="Representing the working class"),
        Candidate(candidate_id="NAGISA", name="Jose Garcia", party="Independent", description="Independent candidate for change"),
        Candidate(candidate_id="KABANATA", name="Ana Reyes", party="Reform Party", description="Modernization and progress"),
        Candidate(candidate_id="BAGONG_LUZON", name="Pedro Martinez", party="New Alliance", description="Unity and progression"),
    ]

    for candidate in candidates:
        db.add(candidate)
    db.commit()