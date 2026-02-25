"""
Firebase State Management
Handles all Firebase operations for real-time state and trade history.
"""
import firebase_admin
from firebase_admin import credentials, firestore, exceptions
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime
import json

class FirebaseManager:
    """Manages Firebase Firestore connections and operations."""
    
    def __init__(self, firebase_config):
        """Initialize Firebase connection with error handling."""
        self._db: Optional[firestore.Client] = None
        self._initialized = False
        
        try:
            if not firebase_admin._apps:
                cred_dict = {
                    "type": "service_account",
                    "project_id": firebase_config.project_id,
                    "private_key_id": firebase_config.private_key_id,
                    "private_key": firebase_config.private_key,
                    "client_email": firebase_config.client_email,
                    "client_id": firebase_config.client_id,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{firebase_config.client_email}"
                }
                
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
            
            self._db = firestore.client()
            self._initialized = True
            logging.info("Firebase initialized successfully")
            
        except Exception as e:
            logging.error(f"Firebase initialization failed: {e}")
            self._initialized = False
    
    def is_connected(self) -> bool:
        """Check if Firebase is connected."""
        return self._initialized and self._db is not None
    
    def save_trade(self, trade_data: Dict[str, Any]) -> bool:
        """Save a trade to Firestore with validation."""
        if not self.is_connected():
            logging.warning("Firebase not connected - trade not saved")
            return False
        
        try:
            required_fields = ['symbol', 'action', 'quantity', 'price', 'timestamp']
            if not all(field in trade_data for field in required_fields):
                logging.error(f"Missing required trade fields: {required_fields}")
                return False
            
            # Add metadata
            trade_data['created_at'] = datetime.utcnow()
            trade_data['status'] = 'completed'
            
            # Store in trades collection
            trades_ref = self._db.collection('trades')
            trades_ref.add(trade_data)
            
            logging.info(f"Trade saved: {trade_data['symbol']} {trade_data['action']}")
            return True
            
        except exceptions.FirebaseError as e:
            logging.error(f"Firebase error saving trade: {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error saving trade: {e}")
            return False
    
    def get_portfolio_state(self) -> Dict[str, Any]:
        """Retrieve current portfolio state from Firestore."""
        if not self.is_connected