import hmac
import hashlib
import json
import time
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("blockchain")

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def calculate_file_hmac(data: str) -> str:
    """Calculate HMAC-SHA256 for data integrity"""
    secret = os.getenv("TURSO_AUTH_TOKEN", "change-this-in-production!")
    return hmac.new(
        secret.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()

class Block:
    def __init__(self, index: int, timestamp: float, transactions: List[Dict], previous_hash: str, nonce: int = 0, hash: str = ""):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = hash if hash else self.calculate_hash()
    
    def calculate_hash(self) -> str:
        block_data = {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }
        block_string = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "timestamp_readable": datetime.fromtimestamp(self.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Block':
        return cls(
            index=data["index"],
            timestamp=data["timestamp"],
            transactions=data["transactions"],
            previous_hash=data["previous_hash"],
            nonce=data["nonce"],
            hash=data["hash"]
        )

class Blockchain:
    DIFFICULTY = 2
    MINING_REWARD = 0.0
    VOTES_PER_BLOCK = 5
    TRANSACTION_GAS_COST = 0.05
    
    def __init__(self):
        self.chain: List[Block] = []
        self.pending_transactions: List[Dict] = []
        self.participants: Dict[str, float] = {}
        self.load_from_db()
    
    def create_genesis_block(self) -> Block:
        genesis_block = Block(
            index=0,
            timestamp=time.time(),
            transactions=[{
                "type": "genesis",
                "data": "Genesis Block - Blockchain Voting System Initialized",
                "timestamp": time.time()
            }],
            previous_hash="0",
            nonce=0
        )
        genesis_block.hash = genesis_block.calculate_hash()
        return genesis_block
    
    def add_participant(self, resident_id: str, initial_gas: float = 1.0):
        self.participants[resident_id] = initial_gas
    
    def get_gas_balance(self, resident_id: str) -> float:
        return self.participants.get(resident_id, 0.0)
    
    def deduct_gas(self, resident_id: str) -> bool:
        if self.participants.get(resident_id, 0.0) >= self.TRANSACTION_GAS_COST:
            self.participants[resident_id] -= self.TRANSACTION_GAS_COST
            return True
        return False
    
    def add_transaction(self, transaction: Dict[str, Any]) -> bool:
        if transaction.get("type") == "vote":
            resident_id = transaction.get("resident_id")
            if not self.deduct_gas(resident_id):
                return False
            
        transaction["timestamp"] = time.time()
        self.pending_transactions.append(transaction)
        return True
    
    def mine_pending_transactions(self, miner_address: str = "system") -> Optional[Block]:
        if len(self.pending_transactions) < self.VOTES_PER_BLOCK:
            return None
        
        votes_to_mine = self.pending_transactions[:self.VOTES_PER_BLOCK]
        
        previous_hash = self.chain[-1].hash if self.chain else "0"
        new_block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            transactions=votes_to_mine,
            previous_hash=previous_hash,
            nonce=0
        )
        
        new_block = self.proof_of_work(new_block)
        self.chain.append(new_block)
        
        self.pending_transactions = self.pending_transactions[self.VOTES_PER_BLOCK:]
        
        self.create_backup()
        self.save_to_db()
        return new_block
    
    def proof_of_work(self, block: Block) -> Block:
        target = "0" * self.DIFFICULTY
        while not block.hash.startswith(target):
            block.nonce += 1
            block.hash = block.calculate_hash()
        return block
    
    def is_chain_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            if current_block.hash != current_block.calculate_hash():
                return False
            
            if current_block.previous_hash != previous_block.hash:
                return False
        
        if self.chain:
            genesis = self.chain[0]
            if genesis.previous_hash != "0":
                return False
            if genesis.hash != genesis.calculate_hash():
                return False
        
        return True
    
    def get_transaction_by_hash(self, search_hash: str) -> Optional[Dict[str, Any]]:
        for block in self.chain:
            for tx in block.transactions:
                tx_hash = self._generate_transaction_hash(tx)
                if tx_hash == search_hash:
                    return {
                        **tx,
                        "transaction_hash": tx_hash,
                        "block_index": block.index,
                        "block_hash": block.hash,
                        "confirmed": True
                    }
        
        for tx in self.pending_transactions:
            tx_hash = self._generate_transaction_hash(tx)
            if tx_hash == search_hash:
                return {
                    **tx,
                    "transaction_hash": tx_hash,
                    "confirmed": False,
                    "mempool": True
                }
        
        return None
    
    def _generate_transaction_hash(self, transaction: Dict[str, Any]) -> str:
        tx_data = {
            "resident_id": transaction.get("resident_id"),
            "candidate_id": transaction.get("candidate_id"),
            "position_id": transaction.get("position_id"),
            "timestamp": transaction.get("timestamp"),
            "type": transaction.get("type")
        }
        tx_string = json.dumps(tx_data, sort_keys=True)
        return hashlib.sha256(tx_string.encode()).hexdigest()
    
    def save_to_db(self):
        """Save blockchain data to Turso database"""
        try:
            from libsql_client import create_client_sync
            
            TURSO_URL = os.getenv("TURSO_URL")
            TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN")
            
            if not TURSO_URL:
                logger.warning("TURSO_URL not set")
                return
            
            # Convert libsql:// to https:// for HTTP-based client
            if TURSO_URL.startswith("libsql://"):
                TURSO_URL = TURSO_URL.replace("libsql://", "https://", 1)
            
            # Use synchronous client for libsql
            client = create_client_sync(
                TURSO_URL,
                auth_token=TURSO_AUTH_TOKEN if TURSO_AUTH_TOKEN else None
            )
            
            try:
                # Prepare data
                chain_data = [block.to_dict() for block in self.chain]
                data = {
                    "chain": chain_data,
                    "pending_transactions": self.pending_transactions,
                    "participants": self.participants
                }
                
                json_str = json.dumps(data, indent=2)
                hmac_val = calculate_file_hmac(json_str)
                
                # Create table if not exists
                client.execute("""
                    CREATE TABLE IF NOT EXISTS blockchain_ledger (
                        id INTEGER PRIMARY KEY,
                        chain_data TEXT,
                        pending_transactions TEXT,
                        participants TEXT,
                        hmac TEXT,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Upsert into blockchain_ledger table
                client.execute("""
                    INSERT OR REPLACE INTO blockchain_ledger 
                    (id, chain_data, pending_transactions, participants, hmac, updated_at) 
                    VALUES (1, ?, ?, ?, ?, datetime('now'))
                """, [
                    json_str,
                    json.dumps(self.pending_transactions),
                    json.dumps(self.participants),
                    hmac_val
                ])
                
                logger.info("Ledger saved to Turso DB (%s blocks)", len(self.chain))
                
            finally:
                client.close()
            
        except Exception as e:
            logger.error(f"Failed to save to Turso: {e}")
            self._save_fallback()
    
    def _save_fallback(self):
        """Fallback to local JSON if Turso fails"""
        data = {
            "chain": [block.to_dict() for block in self.chain],
            "pending_transactions": self.pending_transactions,
            "participants": self.participants
        }
        with open("ledger_backup.json", "w") as f:
            json.dump(data, f, indent=2)
        logger.info("Ledger saved to fallback file")
    
    def load_from_db(self):
        """Load blockchain data from Turso database"""
        try:
            from libsql_client import create_client_sync
            
            TURSO_URL = os.getenv("TURSO_URL")
            TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN")
            
            if not TURSO_URL:
                logger.warning("TURSO_URL not set, using local fallback")
                self._load_fallback()
                return
            
            # Convert libsql:// to https:// for HTTP-based client
            if TURSO_URL.startswith("libsql://"):
                TURSO_URL = TURSO_URL.replace("libsql://", "https://", 1)
            
            # Use synchronous client for libsql
            client = create_client_sync(
                TURSO_URL,
                auth_token=TURSO_AUTH_TOKEN if TURSO_AUTH_TOKEN else None
            )
            
            try:
                # Create table if not exists
                client.execute("""
                    CREATE TABLE IF NOT EXISTS blockchain_ledger (
                        id INTEGER PRIMARY KEY,
                        chain_data TEXT,
                        pending_transactions TEXT,
                        participants TEXT,
                        hmac TEXT,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Load ledger
                result = client.execute("SELECT chain_data, pending_transactions, participants, hmac FROM blockchain_ledger WHERE id = 1")
                
                # FIX: Handle different response formats from libsql-client
                rows = None
                if hasattr(result, 'rows'):
                    rows = result.rows
                elif isinstance(result, list):
                    rows = result
                elif isinstance(result, dict) and 'rows' in result:
                    rows = result.get('rows', [])
                elif hasattr(result, '__iter__'):
                    try:
                        rows = list(result)
                    except:
                        rows = None
                
                if rows and len(rows) > 0:
                    row = rows[0]
                    
                    try:
                        # FIX: Handle dict, Row object, and tuple response formats
                        chain_json = None
                        pending_json = None
                        participants_json = None
                        stored_hmac = None
                        
                        # Try dict-like access first (works for dict and libsql Row)
                        try:
                            # libsql Row objects support both [] and .get()
                            if hasattr(row, 'get') and callable(row.get):
                                chain_json = row.get('chain_data')
                                pending_json = row.get('pending_transactions')
                                participants_json = row.get('participants')
                                stored_hmac = row.get('hmac')
                            elif hasattr(row, '__getitem__'):
                                # Assume it's a dict or supports indexing
                                chain_json = row['chain_data'] if isinstance(row, dict) else row[0]
                                pending_json = row['pending_transactions'] if isinstance(row, dict) else row[1]
                                participants_json = row['participants'] if isinstance(row, dict) else row[2]
                                stored_hmac = row['hmac'] if isinstance(row, dict) else row[3]
                        except (KeyError, IndexError, TypeError) as e:
                            # Fallback: try positional access
                            if isinstance(row, (list, tuple)) and len(row) >= 4:
                                chain_json = row[0]
                                pending_json = row[1]
                                participants_json = row[2]
                                stored_hmac = row[3]
                            else:
                                raise ValueError(f"Cannot parse row: {e}, row: {row}")
                        
                        # Verify HMAC
                        if stored_hmac and chain_json:
                            calculated_hmac = calculate_file_hmac(chain_json)
                            if calculated_hmac != stored_hmac:
                                logger.error("HMAC mismatch - ledger may be tampered!")
                                raise Exception("Ledger integrity check failed")
                        
                        data = json.loads(chain_json)
                        self.chain = [Block.from_dict(block_data) for block_data in data]
                        self.pending_transactions = json.loads(pending_json) if pending_json else []
                        self.participants = json.loads(participants_json) if participants_json else {}
                        logger.info(f"Ledger loaded: {len(self.chain)} blocks, {len(self.participants)} participants")
                        
                    except (ValueError, TypeError, KeyError, json.JSONDecodeError) as e:
                        logger.error(f"Error parsing row data: {e}. Row type: {type(row)}")
                        raise Exception(f"Failed to parse ledger data: {e}")
                else:
                    # No ledger found, create genesis block
                    logger.info("No ledger found in database. Creating genesis block...")
                    genesis = self.create_genesis_block()
                    self.chain.append(genesis)
                    self.save_to_db()
                    logger.info("Genesis block created and saved.")
                
            finally:
                client.close()
            
        except Exception as e:
            logger.error(f"Failed to load from Turso: {e}")
            logger.info("Falling back to local backup...")
            self._load_fallback()
    
    def _load_fallback(self):
        """Fallback to local JSON if Turso fails"""
        try:
            with open("ledger_backup.json", "r") as f:
                data = json.load(f)
                self.chain = [Block.from_dict(block_data) for block_data in data.get("chain", [])]
                self.pending_transactions = data.get("pending_transactions", [])
                self.participants = data.get("participants", {})
                logger.info(f"Ledger loaded from backup: {len(self.chain)} blocks")
        except FileNotFoundError:
            logger.info("No backup found. Creating genesis block...")
            genesis = self.create_genesis_block()
            self.chain.append(genesis)
            logger.info("Genesis block created.")
    
    def get_chain_data(self) -> List[Dict[str, Any]]:
        return [block.to_dict() for block in self.chain]
    
    def get_pending_count(self) -> int:
        return len(self.pending_transactions)
    
    def get_block_count(self) -> int:
        return len(self.chain)
    
    def create_backup(self):
        """Create backup of current ledger"""
        try:
            import shutil
            os.makedirs("backups", exist_ok=True)
            backup_file = f"backups/ledger_backup_{int(time.time())}.json"
            data = {
                "chain": [block.to_dict() for block in self.chain],
                "pending_transactions": self.pending_transactions,
                "participants": self.participants
            }
            with open(backup_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Backup failed: {e}")

# Initialize blockchain
blockchain = Blockchain()
