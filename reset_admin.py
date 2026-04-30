import sys
sys.path.insert(0, '.')

from main import SessionLocal, Admin, hash_pin
from datetime import datetime
import secrets

db = SessionLocal()
try:
    # Check if admin table exists
    admin = db.query(Admin).filter(Admin.username == "admin").first()
    if admin:
        print(f"Found admin: {admin.username}")
        admin.password_hash = hash_pin("admin123")
        admin.failed_attempts = 0
        admin.locked_until = None
        admin.is_active = True
        print("Updated password to admin123")
    else:
        print("Creating new admin account...")
        new_admin = Admin(
            username="admin",
            password_hash=hash_pin("admin123"),
            is_active=True,
            created_at=datetime.utcnow().isoformat()
        )
        db.add(new_admin)
        print("Created new admin with password admin123")
    
    db.commit()
    print("SUCCESS! Admin credentials reset.")
    
except Exception as e:
    print(f"Error: {e}")
    print(f"Checking if admins table exists...")
    
    # Try to create table
    from main import Base, engine
    try:
        Base.metadata.create_all(bind=engine)
        print("Created tables. Trying again...")
        
        # Retry
        admin = db.query(Admin).filter(Admin.username == "admin").first()
        if not admin:
            new_admin = Admin(
                username="admin",
                password_hash=hash_pin("admin123"),
                is_active=True,
                created_at=datetime.utcnow().isoformat()
            )
            db.add(new_admin)
            db.commit()
            print("SUCCESS! Created new admin with password admin123")
    except Exception as e2:
        print(f"Second error: {e2}")
        
finally:
    db.close()