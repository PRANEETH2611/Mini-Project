"""
Test MongoDB Connection
Run this script to verify MongoDB setup
"""
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.mongodb_connection import get_database

def test_connection():
    """Test MongoDB connection and basic operations"""
    print("=" * 50)
    print("MongoDB Connection Test")
    print("=" * 50)
    
    try:
        # Initialize database
        print("\n1. Connecting to MongoDB...")
        db = get_database()
        print("   [OK] Connection successful!")
        
        # Test collections
        print("\n2. Checking collections...")
        print(f"   Users: {db.users_collection.count_documents({})} documents")
        print(f"   Incidents: {db.incidents_collection.count_documents({})} documents")
        print(f"   Metrics: {db.metrics_collection.count_documents({})} documents")
        print(f"   Alerts: {db.alerts_collection.count_documents({})} documents")
        
        # Test authentication
        print("\n3. Testing authentication...")
        user = db.authenticate_user("admin", "admin123")
        if user:
            print(f"   [OK] Admin user found: {user['username']} ({user['role']})")
        else:
            print("   [WARN] Admin user not found (will be created on first run)")
        
        # Test data retrieval
        print("\n4. Testing data retrieval...")
        incidents = db.get_incidents(limit=5)
        print(f"   Found {len(incidents)} incidents")
        
        if incidents:
            latest = incidents[0]
            print(f"   Latest incident: {latest.get('timestamp', 'N/A')}")
            print(f"   Alert status: {latest.get('alert_status', 'N/A')}")
        
        # Test statistics
        print("\n5. Testing statistics...")
        stats = db.get_incident_stats()
        if stats:
            print(f"   Total records: {stats.get('total', 0)}")
            print(f"   Alerts: {stats.get('alerts', 0)}")
            print(f"   OK: {stats.get('ok', 0)}")
        else:
            print("   No statistics available (no data in database)")
        
        print("\n" + "=" * 50)
        print("[OK] All tests passed!")
        print("=" * 50)
        print("\n[INFO] Next steps:")
        print("   1. Run: streamlit run dashboard/app.py")
        print("   2. Login as admin")
        print("   3. Import CSV data via Admin dashboard")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        print("\n[INFO] Troubleshooting:")
        print("   1. Make sure MongoDB is running")
        print("   2. Check connection string in mongodb_connection.py")
        print("   3. See README_MONGODB.md for setup instructions")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
