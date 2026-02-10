"""
MongoDB Connection and Database Utilities
"""
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from datetime import datetime
import pandas as pd

class MongoDBConnection:
    """MongoDB Connection Manager"""
    
    def __init__(self, connection_string=None, database_name="aiops_db"):
        """
        Initialize MongoDB connection
        
        Args:
            connection_string: MongoDB connection string (default: mongodb://localhost:27017/)
            database_name: Name of the database to use
        """
        # Default connection string if not provided
        if connection_string is None:
            connection_string = os.getenv(
                'MONGODB_URI', 
                'mongodb://localhost:27017/'
            )
        
        self.connection_string = connection_string
        self.database_name = database_name
        self.client = None
        self.db = None
        self._connect()
    
    def _connect(self):
        """Establish connection to MongoDB"""
        try:
            self.client = MongoClient(
                self.connection_string,
                serverSelectionTimeoutMS=5000  # 5 second timeout
            )
            # Test connection
            self.client.server_info()
            self.db = self.client[self.database_name]
            print(f"[OK] Connected to MongoDB: {self.database_name}")
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"[ERROR] MongoDB connection failed: {e}")
            print("[INFO] Make sure MongoDB is running on your system")
            raise
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("[INFO] MongoDB connection closed")
    
    def get_collection(self, collection_name):
        """Get a collection from the database"""
        return self.db[collection_name]
    
    def test_connection(self):
        """Test if connection is alive"""
        try:
            self.client.server_info()
            return True
        except:
            return False


class AIOpsDatabase:
    """AIOps Database Operations"""
    
    def __init__(self, connection_string=None):
        self.mongo = MongoDBConnection(connection_string)
        self.users_collection = self.mongo.get_collection("users")
        self.incidents_collection = self.mongo.get_collection("incidents")
        self.metrics_collection = self.mongo.get_collection("metrics")
        self.alerts_collection = self.mongo.get_collection("alerts")
        self._initialize_collections()
    
    def _initialize_collections(self):
        """Initialize collections with default data if empty"""
        # Create indexes
        self.incidents_collection.create_index("timestamp")
        self.metrics_collection.create_index("timestamp")
        self.alerts_collection.create_index("timestamp")
        self.users_collection.create_index("username", unique=True)
        
        # Insert default users if collection is empty
        if self.users_collection.count_documents({}) == 0:
            default_users = [
                {
                    "username": "admin",
                    "password": "admin123",  # In production, use hashed passwords
                    "role": "ADMIN",
                    "email": "admin@aiops.com",
                    "created_at": datetime.now(),
                    "is_active": True
                },
                {
                    "username": "user",
                    "password": "user123",
                    "role": "USER",
                    "email": "user@aiops.com",
                    "created_at": datetime.now(),
                    "is_active": True
                }
            ]
            self.users_collection.insert_many(default_users)
            print("[OK] Default users created")
    
    # User Operations
    def authenticate_user(self, username, password):
        """Authenticate user"""
        user = self.users_collection.find_one({
            "username": username,
            "password": password,
            "is_active": True
        })
        if user:
            # Remove password from response
            user.pop('password', None)
            user['_id'] = str(user['_id'])
            return user
        return None
    
    def get_user(self, username):
        """Get user by username"""
        user = self.users_collection.find_one({"username": username})
        if user:
            user.pop('password', None)
            user['_id'] = str(user['_id'])
        return user
    
    def create_user(self, user_data):
        """Create new user"""
        user_data['created_at'] = datetime.now()
        user_data['is_active'] = True
        result = self.users_collection.insert_one(user_data)
        return str(result.inserted_id)
    
    def update_user(self, username, update_data):
        """Update user"""
        update_data['updated_at'] = datetime.now()
        result = self.users_collection.update_one(
            {"username": username},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    def get_all_users(self):
        """Get all users (admin only)"""
        users = list(self.users_collection.find({}))
        for user in users:
            user.pop('password', None)
            user['_id'] = str(user['_id'])
        return users
    
    # Incident Operations
    def insert_incident(self, incident_data):
        """Insert incident data"""
        incident_data['created_at'] = datetime.now()
        result = self.incidents_collection.insert_one(incident_data)
        return str(result.inserted_id)
    
    def insert_incidents_bulk(self, incidents_list):
        """Insert multiple incidents"""
        for incident in incidents_list:
            incident['created_at'] = datetime.now()
        result = self.incidents_collection.insert_many(incidents_list)
        return len(result.inserted_ids)
    
    def get_incidents(self, filters=None, limit=1000, sort_by="timestamp", sort_order=-1):
        """Get incidents with filters"""
        if filters is None:
            filters = {}
        
        cursor = self.incidents_collection.find(filters).sort(sort_by, sort_order).limit(limit)
        incidents = list(cursor)
        
        # Convert ObjectId to string
        for incident in incidents:
            incident['_id'] = str(incident['_id'])
            if 'created_at' in incident:
                incident['created_at'] = incident['created_at'].isoformat()
            if 'timestamp' in incident:
                if isinstance(incident['timestamp'], datetime):
                    incident['timestamp'] = incident['timestamp'].isoformat()
        
        return incidents
    
    def get_latest_incident(self):
        """Get latest incident"""
        incident = self.incidents_collection.find_one(
            {},
            sort=[("timestamp", -1)]
        )
        if incident:
            incident['_id'] = str(incident['_id'])
            if 'timestamp' in incident and isinstance(incident['timestamp'], datetime):
                incident['timestamp'] = incident['timestamp'].isoformat()
        return incident
    
    def get_incident_stats(self, filters=None):
        """Get incident statistics"""
        if filters is None:
            filters = {}
        
        pipeline = [
            {"$match": filters},
            {"$group": {
                "_id": None,
                "total": {"$sum": 1},
                "alerts": {"$sum": {"$cond": [{"$eq": ["$alert_status", "ALERT"]}, 1, 0]}},
                "ok": {"$sum": {"$cond": [{"$eq": ["$alert_status", "OK"]}, 1, 0]}},
                "anomalies": {"$sum": {"$cond": [{"$eq": ["$anomaly_label", 1]}, 1, 0]}},
                "avg_cpu": {"$avg": "$cpu_usage"},
                "avg_memory": {"$avg": "$memory_usage"},
                "avg_response": {"$avg": "$response_time"},
                "avg_failure_prob": {"$avg": "$failure_probability"}
            }}
        ]
        
        result = list(self.incidents_collection.aggregate(pipeline))
        return result[0] if result else {}
    
    def get_root_cause_distribution(self, filters=None):
        """Get root cause distribution"""
        if filters is None:
            filters = {}
        
        pipeline = [
            {"$match": filters},
            {"$group": {
                "_id": "$predicted_root_cause",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ]
        
        result = list(self.incidents_collection.aggregate(pipeline))
        return {item['_id']: item['count'] for item in result}
    
    # Metrics Operations
    def insert_metrics(self, metrics_data):
        """Insert metrics data"""
        metrics_data['created_at'] = datetime.now()
        result = self.metrics_collection.insert_one(metrics_data)
        return str(result.inserted_id)
    
    def get_metrics(self, filters=None, limit=1000):
        """Get metrics"""
        if filters is None:
            filters = {}
        
        cursor = self.metrics_collection.find(filters).sort("timestamp", -1).limit(limit)
        metrics = list(cursor)
        
        for metric in metrics:
            metric['_id'] = str(metric['_id'])
        
        return metrics
    
    # Alert Operations
    def create_alert(self, alert_data):
        """Create alert"""
        alert_data['created_at'] = datetime.now()
        alert_data['status'] = 'active'
        result = self.alerts_collection.insert_one(alert_data)
        return str(result.inserted_id)
    
    def get_active_alerts(self):
        """Get active alerts"""
        alerts = list(self.alerts_collection.find({"status": "active"}))
        for alert in alerts:
            alert['_id'] = str(alert['_id'])
        return alerts
    
    def close_alert(self, alert_id):
        """Close an alert"""
        result = self.alerts_collection.update_one(
            {"_id": alert_id},
            {"$set": {"status": "closed", "closed_at": datetime.now()}}
        )
        return result.modified_count > 0
    
    # Data Import from CSV
    def import_csv_to_mongodb(self, csv_path):
        """Import CSV data to MongoDB"""
        try:
            df = pd.read_csv(csv_path)
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            
            # Convert DataFrame to list of dictionaries
            records = df.to_dict('records')
            
            # Insert into incidents collection
            count = self.insert_incidents_bulk(records)
            print(f"[OK] Imported {count} records from CSV to MongoDB")
            return count
        except Exception as e:
            print(f"[ERROR] Error importing CSV: {e}")
            return 0
    
    def close(self):
        """Close database connection"""
        self.mongo.close()


# Singleton instance
_db_instance = None

def get_database(connection_string=None):
    """Get database instance (singleton pattern)"""
    global _db_instance
    if _db_instance is None:
        _db_instance = AIOpsDatabase(connection_string)
    return _db_instance
