import hmac
import hashlib
import json
import time
import os
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('blockchain')

from dotenv import load_dotenv
load_dotenv()

def calculate_file_hmac(data: str) -> str:
    secret = os.getenv('HMAC_SECRET', 'blockchain-voting-hmac-secret-2026-change-in-production!')
    return hmac.new(secret.encode(), data.encode(), hashlib.sha256).hexdigest()

def turso_request(pipeline: List) -> dict:
    """Send a pipeline request to Turso HTTP API"""
    TURSO_URL = os.getenv('TURSO_URL', '')
    TURSO_AUTH_TOKEN = os.getenv('TURSO_AUTH_TOKEN', '')
    
    if not TURSO_URL:
        return {'error': 'TURSO_URL not set'}
    
    # Convert libsql:// to https://
    if TURSO_URL.startswith('libsql://'):
        TURSO_URL = TURSO_URL.replace('libsql://', 'https://', 1)
    
    url = f"{TURSO_URL}/v2/pipeline"
    headers = {
        "Authorization": f"Bearer {TURSO_AUTH_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {"requests": pipeline}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Turso HTTP request failed: {e}")
        return {'error': str(e)}

class Block:
    def __init__(self, index: int, timestamp: float, transactions: List[Dict], previous_hash: str, nonce: int = 0, hash: str = ''):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = hash if hash else self.calculate_hash()
    
    def calculate_hash(self) -> str:
        block_data = {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': self.transactions,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce
        }
        block_string = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'timestamp_readable': datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S'),
            'transactions': self.transactions,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'hash': self.hash
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Block':
        return cls(
            index=data['index'],
            timestamp=data['timestamp'],
            transactions=data['transactions'],
            previous_hash=data['previous_hash'],
            nonce=data['nonce'],
            hash=data['hash']
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
                'type': 'genesis',
                'data': 'Genesis Block - Blockchain Voting System Initialized',
                'timestamp': time.time()
            }],
            previous_hash='0',
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
        if transaction.get('type') == 'vote':
            resident_id = transaction.get('resident_id')
            if not self.deduct_gas(resident_id):
                return False
        transaction['timestamp'] = time.time()
        self.pending_transactions.append(transaction)
        return True
    
    def mine_pending_transactions(self, miner_address: str = 'system') -> Optional[Block]:
        if len(self.pending_transactions) < self.VOTES_PER_BLOCK:
            return None
        votes_to_mine = self.pending_transactions[:self.VOTES_PER_BLOCK]
        previous_hash = self.chain[-1].hash if self.chain else '0'
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
        target = '0' * self.DIFFICULTY
        while not block.hash.startswith(target):
            block.nonce += 1
            block.hash = block.calculate_hash()
        return block
    
    def is_chain_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
        if self.chain:
            genesis = self.chain[0]
            if genesis.previous_hash != '0':
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
                        'transaction_hash': tx_hash,
                        'block_index': block.index,
                        'block_hash': block.hash,
                        'confirmed': True,
                        'hash': tx_hash
                    }
        for tx in self.pending_transactions:
            tx_hash = self._generate_transaction_hash(tx)
            if tx_hash == search_hash:
                return {
                    **tx,
                    'transaction_hash': tx_hash,
                    'confirmed': False,
                    'mempool': True,
                    'hash': tx_hash
                }
        return None
    
    def _generate_transaction_hash(self, transaction: Dict[str, Any]) -> str:
        tx_data = {
            'resident_id': transaction.get('resident_id'),
            'candidate_id': transaction.get('candidate_id'),
            'position_id': transaction.get('position_id'),
            'timestamp': transaction.get('timestamp'),
            'type': transaction.get('type')
        }
        tx_string = json.dumps(tx_data, sort_keys=True)
        return hashlib.sha256(tx_string.encode()).hexdigest()
    
    def save_to_db(self):
        """Save blockchain to Turso via HTTP API"""
        try:
            chain_data = [block.to_dict() for block in self.chain]
            data = {
                'chain': chain_data,
                'pending_transactions': self.pending_transactions,
                'participants': self.participants
            }
            # Use compact JSON with sorted keys for consistent HMAC calculation
            json_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
            pending_str = json.dumps(self.pending_transactions, sort_keys=True, separators=(',', ':'))
            participants_str = json.dumps(self.participants, sort_keys=True, separators=(',', ':'))
            hmac_val = calculate_file_hmac(json_str)
            
            TURSO_URL = os.getenv('TURSO_URL', '')
            TURSO_AUTH_TOKEN = os.getenv('TURSO_AUTH_TOKEN', '')
            
            if not TURSO_URL:
                logger.warning('TURSO_URL not set')
                self._save_fallback()
                return
            
            # Convert libsql:// to https://
            if TURSO_URL.startswith('libsql://'):
                TURSO_URL = TURSO_URL.replace('libsql://', 'https://', 1)
            
            url = f"{TURSO_URL}/v2/pipeline"
            headers = {
                "Authorization": f"Bearer {TURSO_AUTH_TOKEN}",
                "Content-Type": "application/json"
            }
            
            # Build pipeline: delete old, insert new
            pipeline = [
                {
                    "type": "execute",
                    "stmt": {"sql": "DELETE FROM blockchain_ledger WHERE id = 1"}
                },
                {
                    "type": "execute",
                    "stmt": {
                        "sql": "INSERT INTO blockchain_ledger (id, chain_data, pending_transactions, participants, hmac, updated_at) VALUES (1, ?, ?, ?, ?, datetime('now'))",
                        "args": [
                            {"type": "text", "value": json_str},
                            {"type": "text", "value": pending_str},
                            {"type": "text", "value": participants_str},
                            {"type": "text", "value": hmac_val}
                        ]
                    }
                },
                {"type": "close"}
            ]
            
            payload = {"requests": pipeline}
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            logger.info('Ledger saved to Turso DB (%s blocks)', len(self.chain))
        except Exception as e:
            logger.error(f'Failed to save to Turso: {type(e).__name__}: {e}')
            self._save_fallback()
                return
            
            # Convert libsql:// to https://
            if TURSO_URL.startswith('libsql://'):
                TURSO_URL = TURSO_URL.replace('libsql://', 'https://', 1)
            
            url = f"{TURSO_URL}/v2/pipeline"
            headers = {
                "Authorization": f"Bearer {TURSO_AUTH_TOKEN}",
                "Content-Type": "application/json"
            }
            
            # Build pipeline: create table, delete old, insert new
            pipeline = [
                {
                    "type": "execute",
                    "stmt": {
                        "sql": "CREATE TABLE IF NOT EXISTS blockchain_ledger (id INTEGER PRIMARY KEY, chain_data TEXT, pending_transactions TEXT, participants TEXT, hmac TEXT, updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)"
                    }
                },
                {
                    "type": "execute",
                    "stmt": {
                        "sql": "DELETE FROM blockchain_ledger WHERE id = 1"
                    }
                },
                {
                    "type": "execute",
                    "stmt": {
                        "sql": "INSERT INTO blockchain_ledger (id, chain_data, pending_transactions, participants, hmac, updated_at) VALUES (1, ?, ?, ?, ?, datetime('now'))",
                        "args": [
                            {"type": "text", "value": json_str},
                            {"type": "text", "value": pending_str},
                            {"type": "text", "value": participants_str},
                            {"type": "text", "value": hmac_val}
                        ]
                    }
                },
                {"type": "close"}
            ]
            
            payload = {"requests": pipeline}
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            logger.info('Ledger saved to Turso DB (%s blocks)', len(self.chain))
        except Exception as e:
            logger.error(f'Failed to save to Turso: {type(e).__name__}: {e}')
            self._save_fallback()
    
    def _save_fallback(self):
        data = {
            'chain': [block.to_dict() for block in self.chain],
            'pending_transactions': self.pending_transactions,
            'participants': self.participants
        }
        with open('ledger_backup.json', 'w') as f:
            json.dump(data, f, indent=2)
        logger.info('Ledger saved to fallback file')
    
    def load_from_db(self):
        """Load blockchain from Turso via HTTP API"""
        try:
            TURSO_URL = os.getenv('TURSO_URL', '')
            TURSO_AUTH_TOKEN = os.getenv('TURSO_AUTH_TOKEN', '')
            
            if not TURSO_URL:
                logger.warning('TURSO_URL not set, using local fallback')
                self._load_fallback()
                return
            
            # Convert libsql:// to https://
            if TURSO_URL.startswith('libsql://'):
                TURSO_URL = TURSO_URL.replace('libsql://', 'https://', 1)
            
            url = f"{TURSO_URL}/v2/pipeline"
            headers = {
                "Authorization": f"Bearer {TURSO_AUTH_TOKEN}",
                "Content-Type": "application/json"
            }
            
            # Create table if not exists
            create_payload = {"requests": [
                {"type": "execute", "stmt": {"sql": "CREATE TABLE IF NOT EXISTS blockchain_ledger (id INTEGER PRIMARY KEY, chain_data TEXT, pending_transactions TEXT, participants TEXT, hmac TEXT, updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)"}},
                {"type": "close"}
            ]}
            requests.post(url, json=create_payload, headers=headers, timeout=10)
            
            # Query data
            query_payload = {"requests": [
                {"type": "execute", "stmt": {"sql": "SELECT chain_data, pending_transactions, participants, hmac FROM blockchain_ledger WHERE id = 1"}},
                {"type": "close"}
            ]}
            
            response = requests.post(url, json=query_payload, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Parse response
            results = data.get('results', [])
            if not results:
                logger.info('No ledger found. Creating genesis block...')
                genesis = self.create_genesis_block()
                self.chain.append(genesis)
                self.save_to_db()
                logger.info('Genesis block created and saved.')
                return
            
            first_result = results[0]
            if first_result.get('type') == 'error':
                error_msg = first_result.get('error', {}).get('message', 'Unknown error')
                raise Exception(f"Turso error: {error_msg}")
            
            response_data = first_result.get('response', {})
            result = response_data.get('result', {})
            rows = result.get('rows', [])
            
            logger.info(f'Turso query returned {len(rows)} rows')
            
            if rows and len(rows) > 0:
                row = rows[0]
                try:
                    chain_json = None
                    pending_json = None
                    participants_json = None
                    stored_hmac = None
                    
                    # Handle different row formats
                    if isinstance(row, (tuple, list)):
                        if len(row) >= 4:
                            chain_json = row[0]
                            pending_json = row[1]
                            participants_json = row[2]
                            stored_hmac = row[3]
                    elif isinstance(row, dict):
                        chain_json = row.get('chain_data')
                        pending_json = row.get('pending_transactions')
                        participants_json = row.get('participants')
                        stored_hmac = row.get('hmac')
                    
                    # Ensure chain_json is a string for HMAC calculation
                    if chain_json:
                        if isinstance(chain_json, (dict, list)):
                            chain_json = json.dumps(chain_json, sort_keys=True, separators=(',', ':'))
                        elif not isinstance(chain_json, str):
                            chain_json = str(chain_json)
                    
                    if stored_hmac and chain_json:
                        calculated_hmac = calculate_file_hmac(chain_json)
                        if calculated_hmac != stored_hmac:
                            logger.error('HMAC mismatch - ledger may be tampered!')
                            raise Exception('Ledger integrity check failed')
                    
                    if chain_json:
                        data = json.loads(chain_json)
                        self.chain = [Block.from_dict(block_data) for block_data in data.get('chain', [])]
                        self.pending_transactions = data.get('pending_transactions', [])
                        self.participants = data.get('participants', {})
                        logger.info(f'Ledger loaded: {len(self.chain)} blocks, {len(self.participants)} participants')
                    else:
                        raise Exception('No chain data found')
                except Exception as e:
                    logger.error(f'Error parsing row data: {e}')
                    raise
            else:
                logger.info('No ledger found. Creating genesis block...')
                genesis = self.create_genesis_block()
                self.chain.append(genesis)
                self.save_to_db()
                logger.info('Genesis block created and saved.')
        except Exception as e:
            logger.error(f'Failed to load from Turso: {type(e).__name__}: {e}')
            logger.info('Falling back to local backup...')
            self._load_fallback()
                return
            
            # Convert libsql:// to https://
            if TURSO_URL.startswith('libsql://'):
                TURSO_URL = TURSO_URL.replace('libsql://', 'https://', 1)
            
            url = f"{TURSO_URL}/v2/pipeline"
            headers = {
                "Authorization": f"Bearer {TURSO_AUTH_TOKEN}",
                "Content-Type": "application/json"
            }
            
            # Create table if not exists
            create_payload = {"requests": [
                {"type": "execute", "stmt": {"sql": "CREATE TABLE IF NOT EXISTS blockchain_ledger (id INTEGER PRIMARY KEY, chain_data TEXT, pending_transactions TEXT, participants TEXT, hmac TEXT, updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)"}},
                {"type": "close"}
            ]}
            requests.post(url, json=create_payload, headers=headers, timeout=10)
            
            # Query data
            query_payload = {"requests": [
                {"type": "execute", "stmt": {"sql": "SELECT chain_data, pending_transactions, participants, hmac FROM blockchain_ledger WHERE id = 1"}},
                {"type": "close"}
            ]}
            
            response = requests.post(url, json=query_payload, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Parse response
            results = data.get('results', [])
            if not results:
                logger.info('No ledger found. Creating genesis block...')
                genesis = self.create_genesis_block()
                self.chain.append(genesis)
                self.save_to_db()
                logger.info('Genesis block created and saved.')
                return
            
            first_result = results[0]
            if first_result.get('type') == 'error':
                error_msg = first_result.get('error', {}).get('message', 'Unknown error')
                raise Exception(f"SQL error: {error_msg}")
            
            response_data = first_result.get('response', {})
            result = response_data.get('result', {})
            rows = result.get('rows', [])
            
            logger.info(f'Turso query returned {len(rows)} rows')
            
            if rows and len(rows) > 0:
                row = rows[0]
                try:
                    chain_json = None
                    pending_json = None
                    participants_json = None
                    stored_hmac = None
                    
                    # Handle different row formats
                    if isinstance(row, (tuple, list)):
                        if len(row) >= 4:
                            chain_json = row[0]
                            pending_json = row[1]
                            participants_json = row[2]
                            stored_hmac = row[3]
                    elif isinstance(row, dict):
                        chain_json = row.get('chain_data')
                        pending_json = row.get('pending_transactions')
                        participants_json = row.get('participants')
                        stored_hmac = row.get('hmac')
                    
                    # Ensure chain_json is a string for HMAC calculation
                    if chain_json:
                        if isinstance(chain_json, (dict, list)):
                            chain_json = json.dumps(chain_json)
                        elif not isinstance(chain_json, str):
                            chain_json = str(chain_json)
                    
                    if stored_hmac and chain_json:
                        calculated_hmac = calculate_file_hmac(chain_json)
                        if calculated_hmac != stored_hmac:
                            logger.error('HMAC mismatch - ledger may be tampered!')
                            raise Exception('Ledger integrity check failed')
                    
                    if chain_json:
                        data = json.loads(chain_json)
                        self.chain = [Block.from_dict(block_data) for block_data in data.get('chain', [])]
                        self.pending_transactions = data.get('pending_transactions', [])
                        self.participants = data.get('participants', {})
                        logger.info(f'Ledger loaded: {len(self.chain)} blocks, {len(self.participants)} participants')
                    else:
                        raise Exception('No chain data found')
                except Exception as e:
                    logger.error(f'Error parsing row data: {e}')
                    raise
            else:
                logger.info('No ledger found. Creating genesis block...')
                genesis = self.create_genesis_block()
                self.chain.append(genesis)
                self.save_to_db()
                logger.info('Genesis block created and saved.')
        except Exception as e:
            logger.error(f'Failed to load from Turso: {type(e).__name__}: {e}')
            logger.info('Falling back to local backup...')
            self._load_fallback()
    
    def _load_fallback(self):
        try:
            with open('ledger_backup.json', 'r') as f:
                data = json.load(f)
                self.chain = [Block.from_dict(block_data) for block_data in data.get('chain', [])]
                self.pending_transactions = data.get('pending_transactions', [])
                self.participants = data.get('participants', {})
                logger.info(f'Ledger loaded from backup: {len(self.chain)} blocks')
        except FileNotFoundError:
            logger.info('No backup found. Creating genesis block...')
            genesis = self.create_genesis_block()
            self.chain.append(genesis)
            logger.info('Genesis block created.')
    
    def get_chain_data(self) -> List[Dict[str, Any]]:
        return [block.to_dict() for block in self.chain]
    
    def get_pending_count(self) -> int:
        return len(self.pending_transactions)
    
    def get_block_count(self) -> int:
        return len(self.chain)
    
    def create_backup(self):
        try:
            import shutil
            os.makedirs('backups', exist_ok=True)
            backup_file = f'backups/ledger_backup_{int(time.time())}.json'
            data = {
                'chain': [block.to_dict() for block in self.chain],
                'pending_transactions': self.pending_transactions,
                'participants': self.participants
            }
            with open(backup_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f'Backup failed: {e}')

blockchain = Blockchain()
