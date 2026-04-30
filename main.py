from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import secrets
import string
import hashlib
import json
import time
import os
import logging
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False
    print("Warning: bcrypt not installed. PIN security reduced.")

# SQLAlchemy ORM Setup
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, Float
from sqlalchemy.orm import sessionmaker, declarative_base

# Token Persistence
TOKEN_FILE = "tokens.json"

def load_tokens():
    """Load tokens from JSON file if exists"""
    try:
        if Path(TOKEN_FILE).exists():
            with open(TOKEN_FILE, "r") as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading tokens: {e}")
    return {}

def save_tokens():
    """Save tokens to JSON file"""
    try:
        with open(TOKEN_FILE, "w") as f:
            json.dump(tokens, f)
    except Exception as e:
        Offer(f"Error saving tokens: {e}")

# Initialize tokens
tokens = load_tokens()
print(f"Loaded {len(tokens)} tokens from file")

def purge_expired_tokens():
    """Remove expired tokens and persist the updated store"""
    global tokens
    now = time.time()
    expired = [t for t, data in list(tokens.items()) if data.get("expires_at", 0) <= now]
    if expired:
        for t in expired:
            tokens.pop(t, None)
        save_tokens()
        print(f"Purged {len(expired)} expired tokens")

# Purge expired tokens on startup to ensure a clean state
purge_expired_tokens()

# Turso Database Configuration
DATABASE_URL = os.getenv("TURSO_URL")
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN")

if not DATABASE_URL:
    print("WARNING: TURSO_URL not set, falling back to SQLite")
    DATABASE_URL = "sqlite:///./votechain.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # For Turso, we need to use libsql-client with SQLAlchemy
    try:
        from sqlalchemy import event
        from libsql_client import connect
        
        def _connect(dbapi_connection, connection_record):
            dbapi_connection.connection = connect(
                DATABASE_URL,
                auth_token=TURSO_AUTH_TOKEN if TURSO_AUTH_TOKEN else None
            )
        
        engine = create_engine(
            "sqlite://",  # Placeholder, actual connection handled by event
            connect_args={"check_same_thread": False}
        )
        event.listen(engine, "connect", _connect)
    except ImportError:
        print("WARNING: libsql-client not installed, falling back to SQLite")
        DATABASE_URL = "sqlite:///./votechain.db"
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI(title="Blockchain Voting System", version="1.0.0",
              docs_url="/docs",
              redoc_url="/redoc",
              openapi_url="/openapi.json")

# CORS Configuration - Allow all origins (or set your Vercel URL)
# For production, replace "*" with your actual Vercel URL
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


DEVELOPMENT_MODE = True


# SQLAlchemy Models
class Voter(Base):
    __tablename__ = "voters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    resident_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    
    # ID Verification Fields
    id_type = Column(String(50), nullable=True)  # PhilSys, DriverLicense, Passport, SeniorCitizen, PWD
    id_number = Column(String(100), nullable=True)
    id_photo_front = Column(Text, nullable=True)  # Base64 encoded
    id_photo_back = Column(Text, nullable=True)
    
    # Verification Status
    verification_status = Column(String(20), default='pending')  # pending, under_review, approved, rejected
    rejection_reason = Column(String(255), nullable=True)
    admin_notes = Column(Text, nullable=True)
    verified_by = Column(String(50), nullable=True)
    
    # Flags
    is_verified = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)  # FALSE until admin approves
    consent_given = Column(Boolean, default=False)
    is_flagged = Column(Boolean, default=False)
    
    # PIN Fields
    pin_hash = Column(String(255), nullable=True)
    pin_set_at = Column(String(50), nullable=True)
    pin_setup_token = Column(String(255), nullable=True)
    pin_setup_expires = Column(String(50), nullable=True)
    
    created_at = Column(String(50), default=lambda: datetime.utcnow().isoformat())
    approved_at = Column(String(50), nullable=True)
    
    # Gas balance for voting fees
    gas_balance = Column(Float, default=1.0)


class ElectionOfficial(Base):
    __tablename__ = "election_officials"

    id = Column(Integer, primary_key=True, autoincrement=True)
    official_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    pin_hash = Column(String(255), nullable=True)
    role = Column(String(50), default='officer')  # commissioner, officer
    is_active = Column(Boolean, default=False)
    is_pin_set = Column(Boolean, default=False)
    failed_attempts = Column(Integer, default=0)
    locked_until = Column(String(50), nullable=True)
    created_at = Column(String(50), default=lambda: datetime.utcnow().isoformat())
    last_login = Column(String(50), nullable=True)


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    failed_attempts = Column(Integer, default=0)
    locked_until = Column(String(50), nullable=True)
    created_at = Column(String(50), default=lambda: datetime.utcnow().isoformat())
    last_login = Column(String(50), nullable=True)


class ReviewLock(Base):
    __tablename__ = "review_locks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    voter_resident_id = Column(String(50), unique=True, nullable=False)
    official_id = Column(String(50), nullable=False)
    locked_at = Column(String(50), default=lambda: datetime.utcnow().isoformat())


class VerificationApproval(Base):
    __tablename__ = "verification_approvals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    voter_resident_id = Column(String(50), nullable=False)
    official_id = Column(String(50), nullable=False)
    approved = Column(Boolean, default=False)
    approved_at = Column(String(50), default=lambda: datetime.utcnow().isoformat())


class FlaggedID(Base):
    __tablename__ = "flagged_ids"

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_number = Column(String(100), unique=True, nullable=False)
    id_type = Column(String(50), nullable=True)
    reason = Column(String(255), nullable=True)
    flagged_at = Column(String(50), default=lambda: datetime.utcnow().isoformat())


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    party = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    position_id = Column(Integer, nullable=True)


class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), unique=True, nullable=False)
    max_votes = Column(Integer, default=1)


class PositionUpdate(BaseModel):
    title: Optional[str] = None
    max_votes: Optional[int] = None


class CandidateUpdate(BaseModel):
    name: Optional[str] = None
    party: Optional[str] = None
    description: Optional[str] = None
    position_id: Optional[int] = None


class VoteTransaction(Base):
    __tablename__ = "vote_transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    resident_id = Column(String(50), nullable=False)
    candidate_id = Column(String(50), nullable=False)
    position_id = Column(Integer, nullable=False)
    transaction_hash = Column(String(100), unique=True, nullable=False)
    status = Column(String(20), default="pending")
    created_at = Column(String(50), default=lambda: datetime.utcnow().isoformat())
    block_index = Column(Integer, nullable=True)


def migrate_old_data():
    """Migrate data from old voting.db to new votechain.db"""
    old_db_path = "voting.db"
    
    try:
        # Check if new db already has data - skip migration
        new_db = SessionLocal()
        existing = new_db.query(Voter).first()
        new_db.close()
        if existing:
            return True
        
        # Try migrating from old database
        old_conn = sqlite3.connect(old_db_path)
        old_cursor = old_conn.cursor()
        
        # Get all voters (no phone_number)
        old_cursor.execute("SELECT resident_id, name, is_verified, is_approved, consent_given FROM voters")
        voters = old_cursor.fetchall()
        
        new_db = SessionLocal()
        for v in voters:
            try:
                voter = Voter(
                    resident_id=v[0],
                    name=v[1],
                    is_verified=bool(v[2]),
                    is_approved=bool(v[3]),
                    consent_given=bool(v[4])
                )
                new_db.add(voter)
            except:
                pass
        new_db.commit()
        new_db.close()
        old_conn.close()
        return True
        
    except Exception as e:
        print(f"Migration note: {e}")
        return False


def ensure_columns():
    """Ensure all required columns exist in the database"""
    try:
        # Use the same database as SQLAlchemy engine
        db_path = "votechain.db"  # Default SQLite file
        if DATABASE_URL.startswith("sqlite:///"):
            db_path = DATABASE_URL.replace("sqlite:///", "")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check existing columns
        cursor.execute("PRAGMA table_info(voters)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Columns to add to voters table
        new_columns = {
            "id_type": ("ALTER TABLE voters ADD COLUMN id_type TEXT", False),
            "id_number": ("ALTER TABLE voters ADD COLUMN id_number TEXT", False),
            "id_photo_front": ("ALTER TABLE voters ADD COLUMN id_photo_front TEXT", False),
            "id_photo_back": ("ALTER TABLE voters ADD COLUMN id_photo_back TEXT", False),
            "verification_status": ("ALTER TABLE voters ADD COLUMN verification_status TEXT DEFAULT 'pending'", False),
            "rejection_reason": ("ALTER TABLE voters ADD COLUMN rejection_reason TEXT", False),
            "admin_notes": ("ALTER TABLE voters ADD COLUMN admin_notes TEXT", False),
            "verified_by": ("ALTER TABLE voters ADD COLUMN verified_by TEXT", False),
            "is_flagged": ("ALTER TABLE voters ADD COLUMN is_flagged INTEGER DEFAULT 0", False),
            "created_at": ("ALTER TABLE voters ADD COLUMN created_at TEXT", False),
            "approved_at": ("ALTER TABLE voters ADD COLUMN approved_at TEXT", False),
            "is_active": ("ALTER TABLE voters ADD COLUMN is_active INTEGER DEFAULT 0", False),
            "pin_hash": ("ALTER TABLE voters ADD COLUMN pin_hash TEXT", False),
            "pin_set_at": ("ALTER TABLE voters ADD COLUMN pin_set_at TEXT", False),
            "pin_setup_token": ("ALTER TABLE voters ADD COLUMN pin_setup_token TEXT", False),
            "pin_setup_expires": ("ALTER TABLE voters ADD COLUMN pin_setup_expires TEXT", False),
            "gas_balance": ("ALTER TABLE voters ADD COLUMN gas_balance FLOAT DEFAULT 1.0", False),
        }
        
        def add_column_if_not_exists(table, column, sql):
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {sql}")
            except Exception as e:
                if "already exists" not in str(e).lower():
                    raise
        
        for col_name, (sql, _) in new_columns.items():
            if col_name not in columns:
                cursor.execute(sql)
                print(f"Added column: {col_name}")
        
        # Create flagged_ids table if not exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='flagged_ids'")
        if not cursor.fetchone():
            cursor.execute("""
                CREATE TABLE flagged_ids (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_number TEXT UNIQUE NOT NULL,
                    id_type TEXT,
                    reason TEXT,
                    flagged_at TEXT
                )
            """)
            print("Created table: flagged_ids")
        
        # Create election_officials table if not exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='election_officials'")
        if not cursor.fetchone():
            cursor.execute("""
                CREATE TABLE election_officials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    official_id TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    pin_hash TEXT,
                    role TEXT DEFAULT 'officer',
                    is_active INTEGER DEFAULT 0,
                    is_pin_set INTEGER DEFAULT 0,
                    failed_attempts INTEGER DEFAULT 0,
                    locked_until TEXT,
                    created_at TEXT,
                    last_login TEXT
                )
            """)
            print("Created table: election_officials")
        
        # Create verification_approvals table if not exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='verification_approvals'")
        if not cursor.fetchone():
            cursor.execute("""
                CREATE TABLE verification_approvals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    voter_resident_id TEXT NOT NULL,
                    official_id TEXT NOT NULL,
                    approved INTEGER DEFAULT 0,
                    approved_at TEXT
                )
            """)
            print("Created table: verification_approvals")
        
        conn.commit()
        conn.close()
        print("Database schema updated successfully")
        return True
        
    except Exception as e:
        print(f"Schema migration error: {e}")
        return False


# PIN Helper Functions
def hash_pin(pin: str) -> str:
    """Hash a PIN using bcrypt"""
    if not BCRYPT_AVAILABLE:
        return hashlib.sha256(pin.encode()).hexdigest()
    return bcrypt.hashpw(pin.encode(), bcrypt.gensalt()).decode()

def verify_pin(pin: str, pin_hash: str) -> bool:
    """Verify a PIN against its hash"""
    if not BCRYPT_AVAILABLE:
        return hashlib.sha256(pin.encode()).hexdigest() == pin_hash
    try:
        return bcrypt.checkpw(pin.encode(), pin_hash.encode())
    except:
        return False

def generate_pin() -> str:
    """Generate a random 6-digit PIN"""
    return str(secrets.randbelow(1000000)).zfill(6)


def seed_data():
    """Initialize database tables and seed data"""
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Seed admin account - update if exists, create if not
        admin = db.query(Voter).filter(Voter.resident_id == "ADMIN001").first()
        if not admin:
            admin = Voter(
                resident_id="ADMIN001",
                name="Administrator",
                id_type="admin",
                id_number="ADMIN001",
                verification_status="approved",
                is_verified=True,
                is_approved=True,
                is_active=True,
                consent_given=True,
                gas_balance=10.0  # Admin gets 10.0 gas
            )
            db.add(admin)
        else:
            admin.id_type = "admin"
            admin.id_number = "ADMIN001"
            admin.is_verified = True
            admin.is_approved = True
            admin.is_active = True
            admin.name = "Administrator"
        
        # Seed test user 2026-0001 - update if exists, create if not
        test_user = db.query(Voter).filter(Voter.resident_id == "2026-0001").first()
        if not test_user:
            test_user = Voter(
                resident_id="2026-0001",
                name="Test Resident",
                id_type="resident_id",
                id_number="2026-0001",
                verification_status="approved",
                is_verified=True,
                is_approved=True,
                is_active=True,
                consent_given=True,
                gas_balance=1.0  # Default gas
            )
            db.add(test_user)
        else:
            test_user.id_type = "resident_id"
            test_user.id_number = "2026-0001"
            test_user.verification_status = "approved"
            test_user.is_verified = True
            test_user.is_approved = True
            test_user.is_active = True
            test_user.name = "Test Resident"
        
        # Seed 5 election officials
        officials = [
            ("OFFICIAL-001", "Commissioner Smith", "commissioner"),
            ("OFFICIAL-002", "Officer Garcia", "officer"),
            ("OFFICIAL-003", "Officer Santos", "officer"),
            ("OFFICIAL-004", "Officer Cruz", "officer"),
            ("OFFICIAL-005", "Officer Reyes", "officer"),
        ]
        
        for off_id, name, role in officials:
            official = db.query(ElectionOfficial).filter(ElectionOfficial.official_id == off_id).first()
            if not official:
                official = ElectionOfficial(
                    official_id=off_id,
                    name=name,
                    role=role,
                    is_active=True,
                    is_pin_set=False,
                    created_at=datetime.utcnow().isoformat()
                )
                db.add(official)
            else:
                official.name = name
                official.role = role
                official.is_active = True
        
        db.commit()
        
        # Seed admin account (only 1 admin)
        admin = db.query(Admin).filter(Admin.username == "admin").first()
        if not admin:
            password = ''.join(secrets.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(16))
            password_hash = hash_pin(password)
            admin = Admin(
                username="admin",
                password_hash=password_hash,
                is_active=True,
                created_at=datetime.utcnow().isoformat()
            )
            db.add(admin)
            db.commit()
            with open("admin_credentials.txt", "w") as f:
                f.write(f'{{"username": "admin", "password": "{password}", "generated_at": "{datetime.utcnow().isoformat()}"}}')
            print(f"\n{'='*60}")
            print("ADMIN CREDENTIALS GENERATED")
            print(f"{'='*60}")
            print(f"Username: admin")
            print(f"Password: {password}")
            print(f"{'='*60}")
            print("Credentials saved to: admin_credentials.txt")
            print("IMPORTANT: Change password after first login!")
            print(f"{'='*60}\n")
        
        # Add to blockchain
        from blockchain import blockchain
        try:
            if 'ADMIN001' not in blockchain.participants:
                blockchain.participants['ADMIN001'] = 10.0
            if '2026-0001' not in blockchain.participants:
                blockchain.participants['2026-0001'] = 1.0
            blockchain.save_to_db()
        except Exception as e:
            print(f"Blockchain update skipped: {e}")
            
    except Exception as e:
        print(f"Seed error: {e}")
        db.rollback()
    finally:
        db.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Run migration and seeding on startup
migrate_old_data()
ensure_columns()
seed_data()

from blockchain import blockchain


class VoterRegistration(BaseModel):
    resident_id: str
    name: str
    id_type: str
    id_number: str
    id_photo_front: Optional[str] = None
    id_photo_back: Optional[str] = None
    consent_given: bool


class VoterRegistrationSimple(BaseModel):
    resident_id: str
    name: str
    consent_given: bool


class VerifyVoterRequest(BaseModel):
    action: str  # "approve" or "reject"
    reason: Optional[str] = None
    notes: Optional[str] = None


class LoginRequest(BaseModel):
    id_type: str = "resident_id"  # resident_id, national_id, passport, drivers_license
    id_number: str


class VoteRequest(BaseModel):
    resident_id: str
    candidate_id: str
    position_id: int
    token: str


class DeleteVoterRequest(BaseModel):
    token: str


class AdminApprove(BaseModel):
    resident_id: str
    approved: bool


class PositionCreate(BaseModel):
    title: str
    max_votes: int = 1


class CandidateCreate(BaseModel):
    candidate_id: str
    name: str
    party: Optional[str] = None
    description: Optional[str] = None
    position_id: int


tokens = {}


def create_token(resident_id: str) -> str:
    token = secrets.token_hex(32)
    expires_at = time.time() + 3600
    tokens[token] = {"resident_id": resident_id, "expires_at": expires_at}
    save_tokens()  # Persist to file
    print(f"Token created for {resident_id}: {token[:20]}...")  # Debug log
    return token


def verify_token(token: str) -> Optional[str]:
    print(f"Verifying token: {token}")  # Debug log
    if token in tokens:
        data = tokens[token]
        print(f"Token data: {data}")  # Debug log
        if data["expires_at"] > time.time():
            return data["resident_id"]
    print("Token invalid or expired")  # Debug log
    return None


@app.options("/api/register")
@app.options("/api/{path:path}")
async def handle_options(path: str = None):
    return JSONResponse(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept, Origin, X-Requested-With",
            "Access-Control-Max-Age": "3600",
        }
    )


@app.post("/api/register")
async def register(request: Request, db: SessionLocal = Depends(get_db)):
    body = await request.body()
    
    if not body:
        return JSONResponse(
            status_code=400,
            content={"detail": "Request body is empty"}
        )
    
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return JSONResponse(
            status_code=400,
            content={"detail": "Invalid JSON format"}
        )
    
    if not isinstance(data, dict):
        return JSONResponse(
            status_code=400,
            content={"detail": "Request body must be a JSON object"}
        )
    
    resident_id = data.get("resident_id", "").strip()
    name = data.get("name", "").strip()
    id_type = data.get("id_type", "")
    id_number = data.get("id_number", "")
    pin = data.get("pin", "")
    consent_given = data.get("consent_given", False)
    
    if not resident_id:
        return JSONResponse(
            status_code=400,
            content={"detail": "Resident ID is required"}
        )
    
    if not name:
        return JSONResponse(
            status_code=400,
            content={"detail": "Name is required"}
        )
    
    if not id_type:
        return JSONResponse(
            status_code=400,
            content={"detail": "ID type is required"}
        )
    
    if not id_number:
        return JSONResponse(
            status_code=400,
            content={"detail": "ID number is required"}
        )
    
    if not pin:
        return JSONResponse(
            status_code=400,
            content={"detail": "PIN is required"}
        )
    
    if not pin.isdigit() or len(pin) != 6:
        return JSONResponse(
            status_code=400,
            content={"detail": "PIN must be exactly 6 digits"}
        )
    
    if not consent_given:
        return JSONResponse(
            status_code=400,
            content={"detail": "Data Privacy Act consent is required"}
        )
    
    existing = db.query(Voter).filter(Voter.resident_id == resident_id).first()
    if existing:
        return JSONResponse(
            status_code=400,
            content={"detail": "Resident ID already registered"}
        )
    
    flagged = db.query(FlaggedID).filter(FlaggedID.id_number == id_number).first()
    if flagged:
        return JSONResponse(
            status_code=400,
            content={"detail": "This ID number has been flagged and cannot be registered"}
        )
    
    existing_id = db.query(Voter).filter(Voter.id_number == id_number).first()
    if existing_id:
        return JSONResponse(
            status_code=400,
            content={"detail": "This ID number is already registered to another voter"}
        )
    
    pin_hash = hash_pin(pin)
    now = datetime.utcnow().isoformat()
    
    new_voter = Voter(
        resident_id=resident_id,
        name=name,
        id_type=id_type,
        id_number=id_number,
        id_photo_front=data.get("id_photo_front"),
        id_photo_back=data.get("id_photo_back"),
        pin_hash=pin_hash,
        pin_set_at=now,
        verification_status="pending",
        is_verified=False,
        is_approved=False,
        is_active=False,
        consent_given=True
    )
    
    db.add(new_voter)
    
    try:
        db.commit()
        return {
            "message": "Registration complete. Your PIN is: " + pin + ". Wait for official approval.",
            "resident_id": resident_id,
            "status": "pending_verification",
            "pin_set": True
        }
    except Exception as e:
        db.rollback()
        return JSONResponse(
            status_code=500,
            content={"detail": f"Database error: {str(e)}"}
        )


@app.options("/api/login")
async def login_preflight():
    return JSONResponse(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept, Origin, X-Requested-With",
        }
    )


@app.post("/api/login")
async def login(request: Request, db: SessionLocal = Depends(get_db)):
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"detail": "Invalid JSON body"}
        )
    
    id_type = data.get("id_type", "").strip()
    id_number = data.get("id_number", "").strip()
    pin = data.get("pin", "")
    
    if not id_type:
        return JSONResponse(
            status_code=400,
            content={"detail": "ID type is required"}
        )
    
    if not id_number:
        return JSONResponse(
            status_code=400,
            content={"detail": "ID number is required"}
        )
    
    if not pin:
        return JSONResponse(
            status_code=400,
            content={"detail": "PIN is required"}
        )
    
    if not pin.isdigit() or len(pin) != 6:
        return JSONResponse(
            status_code=400,
            content={"detail": "PIN must be exactly 6 digits"}
        )
    
    flagged = db.query(FlaggedID).filter(
        FlaggedID.id_number == id_number,
        FlaggedID.id_type == id_type
    ).first()
    
    if flagged:
        return JSONResponse(
            status_code=403,
            content={"detail": "This ID has been flagged and cannot be used for voting."}
        )
    
    voter = db.query(Voter).filter(
        Voter.id_type == id_type,
        Voter.id_number == id_number
    ).first()
    
    if not voter:
        return JSONResponse(
            status_code=404,
            content={"detail": "Voter not found with this ID"}
        )
    
    if voter.is_flagged:
        return JSONResponse(
            status_code=403,
            content={"detail": "This voter account is flagged and cannot vote"}
        )
    
    if voter.verification_status == 'pending':
        return JSONResponse(
            status_code=403,
            content={"detail": "Registration is pending verification by election officials"}
        )
    
    if voter.verification_status == 'rejected':
        return JSONResponse(
            status_code=403,
            content={"detail": "Registration was rejected. Contact election officials for assistance."}
        )
    
    if not voter.is_active:
        return JSONResponse(
            status_code=403,
            content={"detail": "Account not yet activated. Please wait for official approval."}
        )
    
    if not voter.pin_hash:
        return JSONResponse(
            status_code=403,
            content={"detail": "PIN not set. Please contact election officials to set your PIN."}
        )
    
    if not verify_pin(pin, voter.pin_hash):
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid PIN"}
        )
    
    token = create_token(voter.resident_id)
    gas_balance = blockchain.get_gas_balance(voter.resident_id)
    
    return {
        "token": token,
        "resident_id": voter.resident_id,
        "name": voter.name,
        "gas_balance": gas_balance,
        "verification_status": voter.verification_status,
        "is_active": voter.is_active,
        "message": "Login successful"
    }


@app.post("/api/voter/setup-pin")
async def voter_setup_pin(request: Request, db: SessionLocal = Depends(get_db)):
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"detail": "Invalid JSON body"}
        )
    
    token_received = data.get("token", "").strip()
    id_type = data.get("id_type", "").strip()
    id_number = data.get("id_number", "").strip()
    new_pin = data.get("new_pin", "")
    
    if not id_type or not id_number or not new_pin:
        return JSONResponse(
            status_code=400,
            content={"detail": "ID type, ID number, and new PIN are required"}
        )
    
    if not new_pin.isdigit() or len(new_pin) != 6:
        return JSONResponse(
            status_code=400,
            content={"detail": "PIN must be exactly 6 digits"}
        )
    
    voter = db.query(Voter).filter(
        Voter.id_type == id_type,
        Voter.id_number == id_number,
        Voter.pin_setup_token == token_received
    ).first()
    
    if not voter:
        return JSONResponse(
            status_code=404,
            content={"detail": "Invalid token or voter not found"}
        )
    
    if voter.pin_hash:
        return JSONResponse(
            status_code=400,
            content={"detail": "PIN already set. Please use your PIN to login."}
        )
    
    if voter.pin_setup_expires:
        try:
            setup_expiry = datetime.fromisoformat(voter.pin_setup_expires)
            if datetime.utcnow() > setup_expiry:
                return JSONResponse(
                    status_code=403,
                    content={"detail": "PIN setup link has expired. Please contact election officials."}
                )
        except:
            return JSONResponse(
                status_code=403,
                content={"detail": "Invalid PIN setup token."}
            )
    
    voter.pin_hash = hash_pin(new_pin)
    voter.pin_set_at = datetime.utcnow().isoformat()
    voter.pin_setup_token = None
    voter.pin_setup_expires = None
    db.commit()
    
    auth_token = create_token(voter.resident_id)
    gas_balance = blockchain.get_gas_balance(voter.resident_id)
    
    return {
        "token": auth_token,
        "resident_id": voter.resident_id,
        "name": voter.name,
        "gas_balance": gas_balance,
        "verification_status": voter.verification_status,
        "is_active": voter.is_active,
        "message": "PIN set successfully"
    }


@app.post("/api/official/login")
async def official_login(request: Request, db: SessionLocal = Depends(get_db)):
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"detail": "Invalid JSON body"}
        )
    
    official_id = data.get("official_id", "").strip()
    pin = data.get("pin", "")
    
    if not official_id:
        return JSONResponse(
            status_code=400,
            content={"detail": "Official ID is required"}
        )
    
    if not pin:
        return JSONResponse(
            status_code=400,
            content={"detail": "PIN is required"}
        )
    
    official = db.query(ElectionOfficial).filter(
        ElectionOfficial.official_id == official_id
    ).first()
    
    if not official:
        return JSONResponse(
            status_code=404,
            content={"detail": "Official not found"}
        )
    
    if not official.is_active:
        return JSONResponse(
            status_code=403,
            content={"detail": "Official account is not active"}
        )
    
    if not official.is_pin_set:
        if not pin.isdigit() or len(pin) != 6:
            return JSONResponse(
                status_code=400,
                content={"detail": "PIN must be exactly 6 digits"}
            )
        official.pin_hash = hash_pin(pin)
        official.is_pin_set = True
        official.last_login = datetime.utcnow().isoformat()
        db.commit()
        token = create_token(official_id)
        return {
            "token": token,
            "official_id": official_id,
            "name": official.name,
            "role": official.role,
            "message": "First login successful. PIN set."
        }
    
    if not verify_pin(pin, official.pin_hash):
        official.failed_attempts += 1
        if official.failed_attempts >= 3:
            official.locked_until = (datetime.utcnow() + timedelta(minutes=15)).isoformat()
        db.commit()
        return JSONResponse(
            status_code=401,
            content={"detail": f"Invalid PIN. {3 - official.failed_attempts} attempts remaining."}
        )
    
    official.failed_attempts = 0
    official.last_login = datetime.utcnow().isoformat()
    db.commit()
    
    token = create_token(official_id)
    return {
        "token": token,
        "official_id": official_id,
        "name": official.name,
        "role": official.role,
        "message": "Login successful"
    }


@app.post("/api/admin/login")
async def admin_login(request: Request, db: SessionLocal = Depends(get_db)):
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"detail": "Invalid JSON body"}
        )
    
    username = data.get("username", "").strip()
    password = data.get("password", "")
    
    if not username:
        return JSONResponse(
            status_code=400,
            content={"detail": "Username is required"}
        )
    
    if not password:
        return JSONResponse(
            status_code=400,
            content={"detail": "Password is required"}
        )
    
    admin = db.query(Admin).filter(Admin.username == username).first()
    
    if not admin:
        return JSONResponse(
            status_code=404,
            content={"detail": "Admin account not found"}
        )
    
    if not admin.is_active:
        return JSONResponse(
            status_code=403,
            content={"detail": "Admin account is disabled"}
        )
    
    if admin.locked_until:
        try:
            lock_time = datetime.fromisoformat(admin.locked_until)
            if datetime.utcnow() < lock_time:
                remaining = (lock_time - datetime.utcnow()).seconds // 60 + 1
                return JSONResponse(
                    status_code=403,
                    content={"detail": f"Account locked. Try again in {remaining} minutes."}
                )
            else:
                admin.locked_until = None
                admin.failed_attempts = 0
        except:
            admin.locked_until = None
    
    if not verify_pin(password, admin.password_hash):
        admin.failed_attempts += 1
        if admin.failed_attempts >= 5:
            admin.locked_until = (datetime.utcnow() + timedelta(minutes=30)).isoformat()
        db.commit()
        remaining = max(0, 5 - admin.failed_attempts)
        return JSONResponse(
            status_code=401,
            content={"detail": f"Invalid password. {remaining} attempts remaining."}
        )
    
    admin.failed_attempts = 0
    admin.last_login = datetime.utcnow().isoformat()
    db.commit()
    
    # Get the admin's voter record to use proper resident_id in token
    admin_voter = db.query(Voter).filter(Voter.id_type == "admin").first()
    admin_resident_id = admin_voter.resident_id if admin_voter else f"admin:{username}"
    
    token = create_token(admin_resident_id)
    return {
        "token": token,
        "username": username,
        "resident_id": admin_resident_id,
        "role": "admin",
        "message": "Login successful"
    }


@app.post("/api/admin/reset-password")
async def reset_admin_password(request: Request, db: SessionLocal = Depends(get_db)):
    """Reset admin password - for development only"""
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"detail": "Invalid JSON body"}
        )
    
    new_username = data.get("username", "admin").strip()
    new_password = data.get("password", "admin123")
    
    try:
        admin = db.query(Admin).filter(Admin.username == new_username).first()
        if admin:
            admin.password_hash = hash_pin(new_password)
            admin.failed_attempts = 0
            admin.locked_until = None
            admin.is_active = True
        else:
            admin = Admin(
                username=new_username,
                password_hash=hash_pin(new_password),
                is_active=True,
                created_at=datetime.utcnow().isoformat()
            )
            db.add(admin)
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Admin password reset to: {new_password}",
            "username": new_username
        }
    except Exception as e:
        db.rollback()
        return JSONResponse(
            status_code=500,
            content={"detail": f"Failed to reset password: {str(e)}"}
        )


@app.post("/api/dev/reset-admin")
async def dev_reset_admin(request: Request, db: SessionLocal = Depends(get_db)):
    """Reset admin password - dev only, no auth required"""
    try:
        data = await request.json()
    except Exception:
        data = {"username": "admin", "password": "admin123"}
    
    new_username = data.get("username", "admin")
    new_password = data.get("password", "admin123")
    
    try:
        admin = db.query(Admin).filter(Admin.username == new_username).first()
        if admin:
            admin.password_hash = hash_pin(new_password)
            admin.failed_attempts = 0
            admin.locked_until = None
            admin.is_active = True
        else:
            admin = Admin(
                username=new_username,
                password_hash=hash_pin(new_password),
                is_active=True,
                created_at=datetime.utcnow().isoformat()
            )
            db.add(admin)
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Admin password reset. Username: {new_username}, Password: {new_password}"
        }
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"detail": str(e)})


@app.post("/api/official/verify-voter/{resident_id}")
async def official_verify_voter(
    resident_id: str,
    request: Request,
    db: SessionLocal = Depends(get_db)
):
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"detail": "Invalid JSON body"}
        )
    
    official_id = data.get("official_id", "")
    action = data.get("action", "")
    
    if not official_id:
        return JSONResponse(
            status_code=400,
            content={"detail": "Official ID is required"}
        )
    
    official = db.query(ElectionOfficial).filter(
        ElectionOfficial.official_id == official_id
    ).first()
    
    if not official:
        return JSONResponse(
            status_code=404,
            content={"detail": "Official not found"}
        )
    
    voter = db.query(Voter).filter(Voter.resident_id == resident_id).first()
    if not voter:
        return JSONResponse(
            status_code=404,
            content={"detail": "Voter not found"}
        )
    
    if voter.verification_status == 'approved' and voter.is_active:
        return JSONResponse(
            status_code=400,
            content={"detail": "Voter already verified"}
        )
    
    if action == "approve":
        voter.verification_status = 'approved'
        voter.is_approved = True
        voter.is_active = True
        voter.verified_by = official_id
        voter.approved_at = datetime.utcnow().isoformat()
        
        approval = VerificationApproval(
            voter_resident_id=resident_id,
            official_id=official_id,
            approved=True,
            approved_at=datetime.utcnow().isoformat()
        )
        db.add(approval)
        db.commit()
        
        return {
            "message": f"Voter {resident_id} has been approved and activated by {official_id}",
            "resident_id": resident_id,
            "status": "approved",
            "is_active": True
        }
    
    elif action == "reject":
        voter.verification_status = 'rejected'
        voter.is_active = False
        
        approval = VerificationApproval(
            voter_resident_id=resident_id,
            official_id=official_id,
            approved=False,
            approved_at=datetime.utcnow().isoformat()
        )
        db.add(approval)
        db.commit()
        
        return {
            "message": f"Voter {resident_id} has been rejected by {official_id}",
            "resident_id": resident_id,
            "status": "rejected"
        }
    
    return JSONResponse(
        status_code=400,
        content={"detail": "Invalid action. Use 'approve' or 'reject'."}
    )


@app.get("/api/official/pending-voters")
async def get_pending_voters(request: Request, db: SessionLocal = Depends(get_db)):
    token = request.query_params.get("token")
    if not token:
        return JSONResponse(
            status_code=401,
            content={"detail": "Token required"}
        )
    
    official_id = verify_token(token)
    if not official_id or not official_id.startswith("OFFICIAL"):
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid or unauthorized token"}
        )
    
    voters = db.query(Voter).filter(
        Voter.verification_status == "pending",
        Voter.consent_given == True
    ).all()
    
    review_locks = db.query(ReviewLock).filter(
        ReviewLock.voter_resident_id.in_([v.resident_id for v in voters])
    ).all()
    
    lock_map = {lock.voter_resident_id: lock.official_id for lock in review_locks}
    official_names = {}
    for v in voters:
        if lock_map.get(v.resident_id):
            o_id = lock_map[v.resident_id]
            if o_id not in official_names:
                official = db.query(ElectionOfficial).filter(ElectionOfficial.official_id == o_id).first()
                official_names[o_id] = official.name if official else o_id
    
    result = []
    for v in voters:
        lock_official_id = lock_map.get(v.resident_id)
        result.append({
            "resident_id": v.resident_id,
            "name": v.name,
            "id_type": v.id_type,
            "id_number": v.id_number,
            "id_photo_front": v.id_photo_front,
            "id_photo_back": v.id_photo_back,
            "verification_status": v.verification_status,
            "is_under_review": lock_official_id is not None,
            "reviewed_by": official_names.get(lock_official_id) if lock_official_id else None,
            "reviewed_by_id": lock_official_id if lock_official_id else None,
            "created_at": v.created_at
        })
    
    return {
        "voters": result,
        "count": len(result)
    }


@app.post("/api/official/start-review/{resident_id}")
async def start_review(resident_id: str, request: Request, db: SessionLocal = Depends(get_db)):
    token = request.query_params.get("token")
    if not token:
        return JSONResponse(
            status_code=401,
            content={"detail": "Token required"}
        )
    
    official_id = verify_token(token)
    if not official_id or not official_id.startswith("OFFICIAL"):
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid or unauthorized token"}
        )
    
    voter = db.query(Voter).filter(Voter.resident_id == resident_id).first()
    if not voter:
        return JSONResponse(
            status_code=404,
            content={"detail": "Voter not found"}
        )
    
    if voter.verification_status != "pending":
        return JSONResponse(
            status_code=400,
            content={"detail": "Voter is not pending verification"}
        )
    
    existing_lock = db.query(ReviewLock).filter(
        ReviewLock.voter_resident_id == resident_id
    ).first()
    
    if existing_lock and existing_lock.official_id != official_id:
        official = db.query(ElectionOfficial).filter(
            ElectionOfficial.official_id == existing_lock.official_id
        ).first()
        reviewer_name = official.name if official else existing_lock.official_id
        return JSONResponse(
            status_code=409,
            content={
                "detail": f"Already being reviewed by {reviewer_name}",
                "reviewed_by": existing_lock.official_id,
                "reviewed_by_name": reviewer_name
            }
        )
    
    if not existing_lock:
        lock = ReviewLock(
            voter_resident_id=resident_id,
            official_id=official_id,
            locked_at=datetime.utcnow().isoformat()
        )
        db.add(lock)
        db.commit()
    
    return {
        "message": "Review started",
        "resident_id": resident_id
    }


@app.post("/api/official/end-review/{resident_id}")
async def end_review(resident_id: str, request: Request, db: SessionLocal = Depends(get_db)):
    token = request.query_params.get("token")
    if not token:
        return JSONResponse(
            status_code=401,
            content={"detail": "Token required"}
        )
    
    official_id = verify_token(token)
    if not official_id or not official_id.startswith("OFFICIAL"):
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid or unauthorized token"}
        )
    
    lock = db.query(ReviewLock).filter(
        ReviewLock.voter_resident_id == resident_id,
        ReviewLock.official_id == official_id
    ).first()
    
    if lock:
        db.delete(lock)
        db.commit()
    
    return {
        "message": "Review ended",
        "resident_id": resident_id
    }


@app.get("/api/admin/voters")
async def get_admin_voters(request: Request, db: SessionLocal = Depends(get_db)):
    token = request.query_params.get("token")
    if not token:
        return JSONResponse(
            status_code=401,
            content={"detail": "Token required"}
        )
    
    resident_id = verify_token(token)
    if not resident_id:
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid token"}
        )
    
    voters = db.query(Voter).filter(Voter.resident_id != 'ADMIN001').all()
    
    result = []
    for v in voters:
        result.append({
            "resident_id": v.resident_id,
            "name": v.name,
            "id_type": v.id_type,
            "id_number": v.id_number,
            "verification_status": v.verification_status,
            "is_active": v.is_active,
            "is_approved": v.is_approved,
            "is_verified": v.is_verified,
            "verified_by": v.verified_by,
            "is_pin_set": bool(v.pin_hash),
            "created_at": v.created_at,
            "approved_at": v.approved_at
        })
    
    return result


@app.post("/api/admin/reset-voter-pin/{resident_id}")
async def admin_reset_pin(
    resident_id: str,
    request: Request,
    db: SessionLocal = Depends(get_db)
):
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"detail": "Invalid JSON body"}
        )
    
    token = data.get("token", "")
    official_id = data.get("official_id", "")
    
    if not token or not verify_token(token):
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid token"}
        )
    
    voter = db.query(Voter).filter(Voter.resident_id == resident_id).first()
    if not voter:
        return JSONResponse(
            status_code=404,
            content={"detail": "Voter not found"}
        )
    
    voter.pin_hash = None
    voter.pin_set_at = None
    voter.is_active = False
    voter.verification_status = 'pending'
    db.commit()
    
    return {
        "message": f"PIN for voter {resident_id} has been reset. Voter must register again with new PIN.",
        "resident_id": resident_id
    }


@app.post("/api/voter/set-pin")
async def voter_set_pin(request: Request, db: SessionLocal = Depends(get_db)):
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"detail": "Invalid JSON body"}
        )
    
    resident_id = data.get("resident_id", "")
    current_pin = data.get("current_pin", "")
    new_pin = data.get("new_pin", "")
    token = data.get("token", "")
    
    if not verify_token(token):
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid token"}
        )
    
    voter = db.query(Voter).filter(Voter.resident_id == resident_id).first()
    if not voter:
        return JSONResponse(
            status_code=404,
            content={"detail": "Voter not found"}
        )
    
    if current_pin and voter.pin_hash:
        if not verify_pin(current_pin, voter.pin_hash):
            return JSONResponse(
                status_code=401,
                content={"detail": "Current PIN is incorrect"}
            )
    
    if not new_pin:
        return JSONResponse(
            status_code=400,
            content={"detail": "New PIN is required"}
        )
    
    if not new_pin.isdigit() or len(new_pin) != 6:
        return JSONResponse(
            status_code=400,
            content={"detail": "PIN must be exactly 6 digits"}
        )
    
    voter.pin_hash = hash_pin(new_pin)
    voter.pin_set_at = datetime.utcnow().isoformat()
    db.commit()
    
    return {
        "message": "PIN changed successfully",
        "pin_set": True
    }


@app.get("/api/candidates")
def get_candidates(db: SessionLocal = Depends(get_db)):
    candidates = db.query(Candidate).all()
    return [{"id": c.id, "candidate_id": c.candidate_id, "name": c.name, "party": c.party, "description": c.description, "position_id": c.position_id} for c in candidates]


@app.get("/api/positions")
def get_positions(db: SessionLocal = Depends(get_db)):
    positions = db.query(Position).all()
    return [{"id": p.id, "title": p.title, "max_votes": p.max_votes} for p in positions]


@app.post("/api/positions")
def create_position(pos: PositionCreate, db: SessionLocal = Depends(get_db)):
    existing = db.query(Position).filter(Position.title == pos.title).first()
    if existing:
        raise HTTPException(status_code=400, detail="Position already exists")
    
    new_pos = Position(title=pos.title, max_votes=pos.max_votes)
    db.add(new_pos)
    db.commit()
    return {"message": "Position created", "id": new_pos.id, "title": new_pos.title}


@app.delete("/api/positions/{position_id}")
def delete_position(position_id: int, db: SessionLocal = Depends(get_db)):
    position = db.query(Position).filter(Position.id == position_id).first()
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    
    db.query(Candidate).filter(Candidate.position_id == position_id).delete()
    db.delete(position)
    db.commit()
    return {"message": "Position deleted"}


@app.post("/api/candidates")
def create_candidate(cand: CandidateCreate, db: SessionLocal = Depends(get_db)):
    existing = db.query(Candidate).filter(Candidate.candidate_id == cand.candidate_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Candidate already exists")
    
    # Verify position exists
    position = db.query(Position).filter(Position.id == cand.position_id).first()
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    
    new_cand = Candidate(
        candidate_id=cand.candidate_id,
        name=cand.name,
        party=cand.party,
        description=cand.description,
        position_id=cand.position_id
    )
    db.add(new_cand)
    db.commit()
    return {"message": "Candidate created", "candidate_id": new_cand.candidate_id}

@app.put("/api/candidates/{candidate_id}")
def update_candidate(candidate_id: int, update: CandidateUpdate, db: SessionLocal = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    if update.name is not None:
        candidate.name = update.name
    if update.party is not None:
        candidate.party = update.party
    if update.description is not None:
        candidate.description = update.description
    if update.position_id is not None:
        candidate.position_id = update.position_id
    db.commit()
    return {"message": "Candidate updated", "candidate_id": candidate.candidate_id}


@app.put("/api/positions/{position_id}")
def update_position(position_id: int, update: PositionUpdate, db: SessionLocal = Depends(get_db)):
    pos = db.query(Position).filter(Position.id == position_id).first()
    if not pos:
        raise HTTPException(status_code=404, detail="Position not found")
    if update.title is not None:
        pos.title = update.title
    if update.max_votes is not None:
        pos.max_votes = update.max_votes
    db.commit()
    return {"message": "Position updated", "id": pos.id, "title": pos.title, "max_votes": pos.max_votes}


@app.put("/api/candidates/{candidate_id}")
def update_candidate(candidate_id: int, update: CandidateUpdate, db: SessionLocal = Depends(get_db)):
    cand = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not cand:
        raise HTTPException(status_code=404, detail="Candidate not found")
    if update.name is not None:
        cand.name = update.name
    if update.party is not None:
        cand.party = update.party
    if update.description is not None:
        cand.description = update.description
    if update.position_id is not None:
        cand.position_id = update.position_id
    db.commit()
    return {"message": "Candidate updated", "id": cand.id, "candidate_id": cand.candidate_id}


@app.post("/api/vote")
def vote(request: VoteRequest, db: SessionLocal = Depends(get_db)):
    resident_id = verify_token(request.token)
    if not resident_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    if resident_id != request.resident_id:
        raise HTTPException(status_code=403, detail="Token mismatch")
    
    voter = db.query(Voter).filter(Voter.resident_id == request.resident_id).first()
    if not voter or not voter.is_verified or not voter.is_approved:
        raise HTTPException(status_code=403, detail="Voter not authorized")
    
    candidate = db.query(Candidate).filter(Candidate.candidate_id == request.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Verify position exists
    position = db.query(Position).filter(Position.id == request.position_id).first()
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    
    # Check max_votes - count all votes (confirmed OR pending) for this position
    vote_count = db.query(VoteTransaction).filter(
        VoteTransaction.resident_id == request.resident_id,
        VoteTransaction.position_id == request.position_id
    ).count()
    
    max_votes = position.max_votes if position.max_votes else 1
    if vote_count >= max_votes:
        raise HTTPException(status_code=400, detail=f"You have already voted for {position.title} (max {max_votes} vote(s) allowed)")
    
    if voter.gas_balance < 0.05:
        raise HTTPException(status_code=400, detail="Insufficient gas balance")
    
    tx_data = {
        "type": "vote",
        "resident_id": request.resident_id,
        "candidate_id": request.candidate_id,
        "position_id": request.position_id,
        "timestamp": time.time()
    }
    
    tx_hash = hashlib.sha256(json.dumps(tx_data, sort_keys=True).encode()).hexdigest()
    
    if not blockchain.add_transaction(tx_data):
        raise HTTPException(status_code=400, detail="Failed to add transaction (insufficient gas)")
    
    # Deduct gas from voter's database balance
    voter.gas_balance = max(0, voter.gas_balance - 0.05)
    logger.info(f"Deducted 0.05 gas from {request.resident_id}, new balance: {voter.gas_balance}")
    
    vote_record = VoteTransaction(
        resident_id=request.resident_id,
        candidate_id=request.candidate_id,
        position_id=request.position_id,
        transaction_hash=tx_hash,
        status="pending"
    )
    db.add(vote_record)
    db.commit()
    
    pending_count = blockchain.get_pending_count()
    mined = False
    
    if pending_count >= 1:
        new_block = blockchain.mine_pending_transactions()
        if new_block:
            mined = True
            # Refresh vote_record from database (may be detached after mining)
            vote_record = db.query(VoteTransaction).filter(
                VoteTransaction.transaction_hash == tx_hash
            ).first()
            if vote_record:
                vote_record.status = "confirmed"
                vote_record.block_index = new_block.index
                db.commit()
    
    return {
        "message": "Vote recorded successfully",
        "transaction_hash": tx_hash,
        "pending_count": pending_count,
        "mined": mined,
        "gas_remaining": voter.gas_balance
    }


@app.get("/api/gas/{resident_id}")
def get_gas(resident_id: str, token: str, db: SessionLocal = Depends(get_db)):
    verified_resident = verify_token(token)
    if not verified_resident or verified_resident != resident_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    voter = db.query(Voter).filter(Voter.resident_id == resident_id).first()
    if not voter:
        raise HTTPException(status_code=404, detail="Voter not found")
    
    return {"resident_id": resident_id, "gas_balance": voter.gas_balance}


@app.get("/api/admin/voters")
def get_voters(token: str, db: SessionLocal = Depends(get_db)):
    admin_resident = verify_token(token)
    if not admin_resident:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    voters = db.query(Voter).filter(Voter.resident_id != 'ADMIN001').all()
    return [{
        "resident_id": v.resident_id,
        "name": v.name,
        "id_type": v.id_type,
        "id_number": v.id_number,
        "verification_status": v.verification_status,
        "is_verified": v.is_verified,
        "is_approved": v.is_approved,
        "is_flagged": v.is_flagged,
        "verified_by": v.verified_by,
        "rejection_reason": v.rejection_reason,
        "created_at": v.created_at if hasattr(v.created_at, 'isoformat') else v.created_at
    } for v in voters]


@app.options("/api/admin/voters/{resident_id}/delete")
async def delete_voter_preflight():
    return JSONResponse(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        }
    )


@app.post("/api/admin/voters/{resident_id}/delete")
def delete_voter(resident_id: str, token: str, db: SessionLocal = Depends(get_db)):
    admin_resident = verify_token(token)
    if not admin_resident:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    voter = db.query(Voter).filter(Voter.resident_id == resident_id).first()
    if not voter:
        raise HTTPException(status_code=404, detail="Voter not found")
    
    if voter.resident_id == 'ADMIN001':
        raise HTTPException(status_code=400, detail="Cannot delete admin account")
    
    db.delete(voter)
    
    from blockchain import blockchain
    if resident_id in blockchain.participants:
        del blockchain.participants[resident_id]
        blockchain.save_to_disk()
    
    db.commit()
    return {"success": True, "message": f"Voter {resident_id} deleted"}


@app.get("/api/admin/verification-queue")
def get_verification_queue(token: str, db: SessionLocal = Depends(get_db)):
    """Get only pending/under_review voters for verification"""
    admin_resident = verify_token(token)
    if not admin_resident:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    voters = db.query(Voter).filter(
        Voter.verification_status.in_(['pending', 'under_review']),
        Voter.resident_id != 'ADMIN001'  # Exclude admin
    ).all()
    
    return [{
        "resident_id": v.resident_id,
        "name": v.name,
        "id_type": v.id_type,
        "id_number": v.id_number,
        "id_photo_front": v.id_photo_front,
        "id_photo_back": v.id_photo_back,
        "verification_status": v.verification_status,
        "verified_by": v.verified_by,
        "created_at": v.created_at if hasattr(v.created_at, 'isoformat') else v.created_at
    } for v in voters]


@app.post("/api/admin/verify-voter/{resident_id}")
def verify_voter(resident_id: str, request: VerifyVoterRequest, token: str, db: SessionLocal = Depends(get_db)):
    """View voter verification status (admin cannot approve - only officials can)"""
    admin_resident = verify_token(token)
    if not admin_resident:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    voter = db.query(Voter).filter(Voter.resident_id == resident_id).first()
    if not voter:
        raise HTTPException(status_code=404, detail="Voter not found")
    
    raise HTTPException(status_code=403, detail="Admin cannot approve voters. Only election officials can verify voters.")


@app.post("/api/admin/approve-all-pending")
def approve_all_pending(token: str, db: SessionLocal = Depends(get_db)):
    """View pending count (admin cannot approve - only officials can)"""
    admin_resident = verify_token(token)
    if not admin_resident:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    raise HTTPException(status_code=403, detail="Admin cannot approve voters. Only election officials can verify voters.")


@app.post("/api/admin/import-voters")
def import_voters(token: str, db: SessionLocal = Depends(get_db)):
    """Import voters from CSV data (sent as JSON array)"""
    admin_resident = verify_token(token)
    if not admin_resident:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # This endpoint expects CSV data as JSON array in request body
    # Format: [{"resident_id": "...", "name": "...", "id_type": "...", "id_number": "..."}, ...]
    import json
    from fastapi import Request
    
    return {"message": "Use POST with JSON array body containing voter data"}


@app.options("/api/admin/import-voters-batch")
async def import_voters_batch_preflight():
    """Handle CORS preflight requests"""
    response = JSONResponse({"status": "ok"})
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


@app.post("/api/admin/import-voters-batch")
def import_voters_batch(request_data: dict, token: str, db: SessionLocal = Depends(get_db)):
    """Import voters from JSON array - trusts the list as pre-verified"""
    admin_resident = verify_token(token)
    if not admin_resident:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    voters_data = request_data.get("voters", [])
    imported = 0
    duplicates = 0
    errors = []
    
    for v in voters_data:
        try:
            voter_pin = v.get("pin", "").strip()
            if not voter_pin:
                errors.append({"resident_id": v.get("resident_id"), "error": "PIN is required"})
                continue
            
            if len(voter_pin) < 4 or len(voter_pin) > 6:
                errors.append({"resident_id": v.get("resident_id"), "error": "PIN must be 4-6 digits"})
                continue
            
            existing = db.query(Voter).filter(Voter.resident_id == v["resident_id"]).first()
            if existing:
                existing.verification_status = "approved"
                existing.is_verified = True
                existing.is_approved = True
                existing.is_active = True
                existing.pin_hash = hash_pin(voter_pin)
                duplicates += 1
                continue
            
            if v.get("id_number"):
                existing_id = db.query(Voter).filter(Voter.id_number == v["id_number"]).first()
                if existing_id:
                    duplicates += 1
                    continue
            
            new_voter = Voter(
                resident_id=v["resident_id"],
                name=v["name"],
                id_type=v.get("id_type", "Pre-verified"),
                id_number=v.get("id_number", ""),
                verification_status="approved",
                is_verified=True,
                is_approved=True,
                is_active=True,
                verified_by=admin_resident,
                approved_at=datetime.utcnow().isoformat(),
                consent_given=True,
                pin_hash=hash_pin(voter_pin)
            )
            db.add(new_voter)
            
            from blockchain import blockchain
            if v["resident_id"] not in blockchain.participants:
                blockchain.add_participant(v["resident_id"], 1.0)
            
            imported += 1
        except Exception as e:
            errors.append({"resident_id": v.get("resident_id"), "error": str(e)})
    
    db.commit()
    blockchain.save_to_disk()
    
    response = JSONResponse({
        "success": True,
        "imported": imported,
        "duplicates": duplicates,
        "errors": errors,
        "message": f"Imported {imported} voters, {duplicates} duplicates skipped"
    })
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


@app.post("/api/admin/flag-id")
def flag_id(request_data: dict, token: str, db: SessionLocal = Depends(get_db)):
    """Manually flag an ID number to prevent registration"""
    admin_resident = verify_token(token)
    if not admin_resident:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    id_number = request_data.get("id_number")
    reason = request_data.get("reason", "Manually flagged by admin")
    
    if not id_number:
        raise HTTPException(status_code=400, detail="ID number required")
    
    # Check if already flagged
    existing = db.query(FlaggedID).filter(FlaggedID.id_number == id_number).first()
    if existing:
        return {"success": True, "message": "ID already flagged", "flagged": True}
    
    flagged = FlaggedID(
        id_number=id_number,
        reason=reason
    )
    db.add(flagged)
    db.commit()
    
    return {"success": True, "message": "ID flagged successfully"}


@app.post("/api/admin/approve")
def approve_voter(request: AdminApprove, token: str, db: SessionLocal = Depends(get_db)):
    admin_resident = verify_token(token)
    if not admin_resident:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    voter = db.query(Voter).filter(Voter.resident_id == request.resident_id).first()
    if not voter:
        raise HTTPException(status_code=404, detail="Voter not found")
    
    voter.is_verified = True
    voter.is_approved = request.approved
    voter.verification_status = "approved" if request.approved else "rejected"
    voter.is_active = request.approved  # Activates voter for login when approved
    voter.verified_by = admin_resident
    
    if request.approved:
        voter.approved_at = datetime.utcnow().isoformat()
        from blockchain import blockchain
        if not any(p.get('resident_id', p) == request.resident_id for p in blockchain.participants):
            blockchain.add_participant(request.resident_id, 1.0)
            blockchain.save_to_db()
    
    db.commit()
    
    return {
        "message": f"Voter {'approved' if request.approved else 'rejected'}",
        "resident_id": request.resident_id,
        "gas_granted": 1.0 if request.approved else 0
    }


@app.get("/api/admin/chain-integrity")
def check_chain_integrity(token: str):
    admin_resident = verify_token(token)
    if not admin_resident:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    is_valid = blockchain.is_chain_valid()
    return {
        "valid": is_valid,
        "block_count": blockchain.get_block_count(),
        "pending_transactions": blockchain.get_pending_count(),
        "participants": len(blockchain.participants)
    }


@app.get("/api/blockchain")
def get_blockchain():
    return {
        "chain": blockchain.get_chain_data(),
        "pending_transactions": blockchain.pending_transactions,
        "participants": blockchain.participants,
        "is_valid": blockchain.is_chain_valid()
    }


@app.get("/api/verify/{tx_hash}")
def verify_transaction(tx_hash: str):
    result = blockchain.get_transaction_by_hash(tx_hash)
    if result:
        return result
    return {"found": False, "message": "Transaction not found"}


@app.get("/api/debug/token-status")
def debug_token_status(token: str):
    """Debug endpoint to check token status"""
    if token in tokens:
        data = tokens[token]
        return {"valid": True, "resident_id": data["resident_id"], "expires_at": data["expires_at"]}
    return {"valid": False, "message": "Token not found"}


@app.get("/api/stats")
def get_stats(db: SessionLocal = Depends(get_db)):
    total_voters = db.query(Voter).count()
    verified_voters = db.query(Voter).filter(Voter.is_verified == True).count()
    approved_voters = db.query(Voter).filter(Voter.is_approved == True).count()
    candidates = db.query(Candidate).count()
    confirmed_votes = db.query(VoteTransaction).filter(VoteTransaction.status == "confirmed").count()
    pending_votes = db.query(VoteTransaction).filter(VoteTransaction.status == "pending").count()
    positions = db.query(Position).count()
    
    return {
        "total_voters": total_voters,
        "verified_voters": verified_voters,
        "approved_voters": approved_voters,
        "candidates": candidates,
        "confirmed_votes": confirmed_votes,
        "pending_votes": pending_votes,
        "positions": positions,
        "block_count": blockchain.get_block_count(),
        "chain_valid": blockchain.is_chain_valid()
    }


@app.get("/api/health")
def health(db: SessionLocal = Depends(get_db)):
    """Basic health check for ledger and token store"""
    try:
        ledger_valid = blockchain.is_chain_valid()
        blocks = blockchain.get_block_count()
        pending = blockchain.get_pending_count()
        tokens_present = Path(TOKEN_FILE).exists()
        return {
            "ledger_valid": ledger_valid,
            "blocks": blocks,
            "pending_transactions": pending,
            "tokens_file_present": tokens_present,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/reset-election")
def reset_election(token: str, db: SessionLocal = Depends(get_db)):
    admin_resident = verify_token(token)
    if not admin_resident:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Clear all votes
    db.query(VoteTransaction).delete()
    
    # Clear all candidates
    db.query(Candidate).delete()
    
    # Clear all positions
    db.query(Position).delete()
    
    # Clear blockchain mempool
    blockchain.pending_transactions = []
    blockchain.save_to_disk()
    
    db.commit()
    
    return {"message": "Election reset successfully"}


@app.get("/api/voted-positions/{resident_id}")
def get_voted_positions(resident_id: str, token: str, db: SessionLocal = Depends(get_db)):
    verified = verify_token(token)
    if not verified or verified != resident_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    voted = db.query(VoteTransaction).filter(
        VoteTransaction.resident_id == resident_id,
    ).all()
    
    return {"voted_position_ids": [v.position_id for v in voted]}


@app.get("/api/voted-candidates/{resident_id}")
def get_voted_candidates(resident_id: str, token: str, db: SessionLocal = Depends(get_db)):
    verified = verify_token(token)
    if not verified or verified != resident_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    voted = db.query(VoteTransaction).filter(
        VoteTransaction.resident_id == resident_id,
        VoteTransaction.status == "confirmed"
    ).all()
    
    # Get position_ids already voted for
    voted_position_ids = list(set([v.position_id for v in voted]))
    
    return {"voted_position_ids": voted_position_ids}


@app.get("/api/vote-status/{resident_id}")
def get_vote_status(resident_id: str, token: str, db: SessionLocal = Depends(get_db)):
    """Get detailed vote status for a voter"""
    verified = verify_token(token)
    if not verified or verified != resident_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    voted = db.query(VoteTransaction).filter(
        VoteTransaction.resident_id == resident_id
    ).all()
    
    return {
        "votes": [{
            "position_id": v.position_id,
            "candidate_id": v.candidate_id,
            "status": v.status,
            "transaction_hash": v.transaction_hash,
            "block_index": v.block_index,
            "confirmed": v.status == "confirmed"
        } for v in voted],
        "total_votes": len(voted),
        "confirmed_count": len([v for v in voted if v.status == "confirmed"]),
        "pending_count": len([v for v in voted if v.status == "pending"])
    }


@app.post("/api/admin/hard-reset")
async def hard_reset_system(token: str, db: SessionLocal = Depends(get_db)):
    """HARD RESET: Wipes ledger, resets voters, clears pending votes.
    WARNING: This is destructive!
    """
    # 1. Verify admin
    admin_resident = verify_token(token)
    if not admin_resident:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # Check if admin (resident_id starts with ADMIN or user is admin)
    admin = db.query(Voter).filter(Voter.resident_id == admin_resident).first()
    if not admin or admin.id_type != "admin":
        raise HTTPException(status_code=401, detail="Admin access required")
    
    try:
        from blockchain import blockchain
        import time
        
        # 2. Wipe ledger.json and recreate genesis block
        blockchain.chain = []
        blockchain.pending_transactions = []
        genesis = blockchain.create_genesis_block()
        blockchain.chain.append(genesis)
        blockchain.participants = {}  # Clear all participants
        logger.info("Ledger wiped. Genesis block recreated.")
        
        # 3. Reset ALL voters in database
        voters = db.query(Voter).all()
        reset_count = 0
        for v in voters:
            v.gas_balance = 1.0  # Reset gas
            reset_count += 1
        
        # 4. Clear ALL vote records
        db.query(VoteTransaction).delete()
        logger.info(f"Cleared {reset_count} voter records")
        
        # 5. Reset participants in blockchain
        blockchain.participants["ADMIN001"] = 10.0
        blockchain.participants["2026-0001"] = 1.0
        blockchain.save_to_disk()
        
        # 6. Save reset timestamp
        reset_time = datetime.utcnow().isoformat()
        with open("last_reset.txt", "w") as f:
            f.write(reset_time)
        
        db.commit()
        
        return {
            "success": True,
            "message": f"HARD RESET COMPLETE. {reset_count} voters reset.",
            "ledger_blocks": 1,
            "votes_cleared": True,
            "gas_reset": True,
            "reset_time": reset_time
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Hard reset failed: {e}")
        raise HTTPException(status_code=500, detail=f"Reset failed: {str(e)}")


@app.options("/api/admin/hard-reset")
async def hard_reset_preflight():
    return JSONResponse(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        }
    )


@app.on_event("startup")
def startup_event():
    # First update database schema (raw SQL for older databases)
    ensure_columns()
    
    # Create all tables if they don't exist (Turso/SQLite)
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created/verified")
    except Exception as e:
        print(f"Warning: Could not create tables via SQLAlchemy: {e}")
    
    # Initialize blockchain (now stored in DB instead of ledger.json)
    # No need to load_from_disk() anymore
    seed_data()
    
    # Sync blockchain participants with database
    db = SessionLocal()
    try:
        voters = db.query(Voter).all()
        for v in voters:
            if v.resident_id not in blockchain.participants:
                blockchain.participants[v.resident_id] = v.gas_balance
        # No need to save_to_disk() - blockchain now uses DB
    except Exception as e:
        print(f"Error syncing blockchain participants: {e}")
    finally:
        db.close()


@app.post("/api/dev/reset-test-accounts")
def reset_test_accounts():
    """Reset test accounts to default state - Development only"""
    if not DEVELOPMENT_MODE:
        raise HTTPException(status_code=403, detail="Development mode only")
    
    db = SessionLocal()
    try:
        # Reset admin
        admin = db.query(Voter).filter(Voter.resident_id == "ADMIN001").first()
        if admin:
            admin.is_verified = True
            admin.is_approved = True
            admin.name = "Administrator"
        
        # Reset test user
        test_user = db.query(Voter).filter(Voter.resident_id == "2026-0001").first()
        if not test_user:
            test_user = Voter(
                resident_id="2026-0001",
                name="Test Resident",
                is_verified=True,
                is_approved=True,
                consent_given=True
            )
            db.add(test_user)
        else:
            test_user.is_verified = True
            test_user.is_approved = True
            test_user.name = "Test Resident"
        
        db.commit()
        
        # Reset blockchain participants
        from blockchain import blockchain
        if not any(p['resident_id'] == 'ADMIN001' for p in blockchain.participants):
            blockchain.add_participant('ADMIN001', 10.0)
        if not any(p['resident_id'] == '2026-0001' for p in blockchain.participants):
            blockchain.add_participant('2026-0001', 1.0)
        blockchain.save_to_db()
        
        return {"message": "Test accounts reset successfully"}
    finally:
        db.close()


# Catch-all route for SPA (must be LAST route)
from fastapi.responses import FileResponse

@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa(full_path: str):
    """Serve index.html for all non-API routes (SPA fallback)"""
    # Let API routes handle their own errors
    if full_path.startswith("api/"):
        return JSONResponse(status_code=404, content={"detail": "API route not found"})
    
    frontend_dist = "frontend/dist"
    index_file = os.path.join(frontend_dist, "index.html")
    
    if os.path.exists(index_file):
        return FileResponse(index_file, media_type="text/html")
    
    return JSONResponse(status_code=404, content={"detail": "Frontend not built"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
