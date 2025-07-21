from flask import Blueprint, jsonify, current_app
from flask_login import login_required
import time
from app.utils.mongo_health import check_mongodb_connection, reconnect_mongodb

bp = Blueprint('debug', __name__)

@bp.route('/health/mongodb')
@login_required
def mongodb_health():
    """Check MongoDB connection health and try to reconnect if needed"""
    start_time = time.time()
    is_healthy, status = check_mongodb_connection()
    
    if not is_healthy:
        # Try to reconnect
        reconnection_success = reconnect_mongodb()
        if reconnection_success:
            is_healthy, status = check_mongodb_connection()
            status = f"Reconnection successful. {status}"
        else:
            status = f"Reconnection failed. {status}"
    
    response_time = time.time() - start_time
    
    # Get MongoDB configuration
    config = {
        'uri': current_app.config.get('MONGODB_URI', 'Not set'),
        'database': current_app.config.get('MONGODB_DB', 'Not set'),
        'server_selection_timeout': current_app.config.get('MONGODB_SERVER_SELECTION_TIMEOUT', 'Not set'),
        'connect_timeout': current_app.config.get('MONGODB_CONNECT_TIMEOUT', 'Not set'),
        'socket_timeout': current_app.config.get('MONGODB_SOCKET_TIMEOUT', 'Not set'),
    }
    
    # Mask credentials in URI for security
    if 'uri' in config and config['uri'] != 'Not set':
        parts = config['uri'].split('@')
        if len(parts) > 1:
            config['uri'] = '***:***@' + parts[1]
    
    return jsonify({
        'status': 'ok' if is_healthy else 'error',
        'mongodb_connected': is_healthy,
        'message': status,
        'response_time': f"{response_time:.2f}s",
        'config': config
    })
