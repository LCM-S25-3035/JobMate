"""
MongoDB Health Check and Reconnection Utilities
"""

from flask import current_app
from pymongo import MongoClient
import time
import logging

logger = logging.getLogger(__name__)

def check_mongodb_connection():
    """
    Check MongoDB connection health
    Returns: tuple (bool, str) - (is_healthy, status_message)
    """
    if not hasattr(current_app, 'mongo_db') or current_app.mongo_db is None:
        return False, "MongoDB connection not initialized"
    
    try:
        # Try to ping the database
        start_time = time.time()
        current_app.mongo_client.admin.command('ping', socketTimeoutMS=10000)
        response_time = time.time() - start_time
        
        # Try to access a collection (jobs) to verify database access
        try:
            jobs_count = current_app.mongo_db.jobs.count_documents({}, limit=1)
            collection_status = f"jobs collection accessible ({jobs_count} document sampled)"
        except Exception as e:
            collection_status = f"jobs collection access error: {str(e)}"
        
        return True, f"MongoDB connected (response time: {response_time:.2f}s, {collection_status})"
    except Exception as e:
        return False, f"MongoDB connection error: {str(e)}"

def reconnect_mongodb():
    """
    Try to reconnect to MongoDB if the connection is lost
    Returns: bool - Whether reconnection was successful
    """
    app = current_app
    mongodb_uri = app.config.get('MONGODB_URI')
    mongodb_db = app.config.get('MONGODB_DB')
    
    if not mongodb_uri or not mongodb_db:
        app.logger.error("Cannot reconnect to MongoDB: Configuration missing")
        return False
    
    try:
        app.logger.info("Attempting to reconnect to MongoDB...")
        
        # Close existing connection if any
        if hasattr(app, 'mongo_client') and app.mongo_client:
            try:
                app.mongo_client.close()
            except:
                pass
        
        # Get timeout settings
        server_selection_timeout = app.config.get('MONGODB_SERVER_SELECTION_TIMEOUT', 30000)
        connect_timeout = app.config.get('MONGODB_CONNECT_TIMEOUT', 30000)
        socket_timeout = app.config.get('MONGODB_SOCKET_TIMEOUT', 60000)
        
        # Create new connection with increased timeouts
        mongo_client = MongoClient(
            mongodb_uri,
            serverSelectionTimeoutMS=server_selection_timeout,
            connectTimeoutMS=connect_timeout,
            socketTimeoutMS=socket_timeout,
            retryWrites=True,
            w='majority',
            maxPoolSize=50,
            maxIdleTimeMS=600000,
            appName='JobMateApp'
        )
        
        # Test connection with increased timeout
        mongo_client.admin.command('ping', socketTimeoutMS=socket_timeout)
        
        # Update app attributes
        app.mongo_client = mongo_client
        app.mongo_db = mongo_client[mongodb_db]
        
        app.logger.info("✅ MongoDB reconnection successful")
        return True
    except Exception as e:
        app.logger.error(f"❌ MongoDB reconnection failed: {str(e)}")
        return False

def safe_mongo_operation(collection_name, operation_type, query=None, data=None, options=None):
    """
    Execute MongoDB operations with automatic reconnection on failure
    
    Args:
        collection_name: Name of the MongoDB collection
        operation_type: Type of operation ('find', 'find_one', 'insert_one', etc.)
        query: Query document for operations like find, find_one, etc.
        data: Data document for operations like insert_one, update_one, etc.
        options: Additional options for the operation
        
    Returns:
        Operation result or None on failure
    """
    app = current_app
    max_retries = 2
    retry_count = 0
    
    if not hasattr(app, 'mongo_db') or app.mongo_db is None:
        app.logger.error(f"Cannot perform MongoDB {operation_type} operation: MongoDB not connected")
        if app.config.get('MONGODB_REQUIRED', True):
            # Try to reconnect once
            if reconnect_mongodb():
                app.logger.info("MongoDB reconnected successfully, retrying operation")
            else:
                app.logger.error("MongoDB reconnection failed, cannot perform operation")
                return None
        else:
            return None
    
    while retry_count <= max_retries:
        try:
            collection = app.mongo_db[collection_name]
            
            if operation_type == 'find':
                return list(collection.find(query or {}, **(options or {})))
            elif operation_type == 'find_one':
                return collection.find_one(query or {}, **(options or {}))
            elif operation_type == 'insert_one':
                return collection.insert_one(data, **(options or {}))
            elif operation_type == 'update_one':
                return collection.update_one(query, data, **(options or {}))
            elif operation_type == 'delete_one':
                return collection.delete_one(query, **(options or {}))
            elif operation_type == 'count_documents':
                return collection.count_documents(query or {}, **(options or {}))
            else:
                app.logger.error(f"Unsupported MongoDB operation type: {operation_type}")
                return None
                
        except Exception as e:
            retry_count += 1
            app.logger.warning(f"MongoDB operation failed (attempt {retry_count}/{max_retries+1}): {str(e)}")
            
            if retry_count <= max_retries:
                # Try to reconnect
                if reconnect_mongodb():
                    app.logger.info("MongoDB reconnected successfully, retrying operation")
                    time.sleep(1)  # Brief pause before retry
                else:
                    app.logger.error("MongoDB reconnection failed")
                    break
            else:
                app.logger.error(f"MongoDB operation failed after {max_retries+1} attempts")
                break
    
    return None
