import sqlite3
import time
import os
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

REQUIRED_FIELDS = {
    "id": str,
    "level": int,
    "country": str,
    "first_session": int,
    "last_session": int,
    "purchase_amount": int,
    "last_purchase_at": int
}


def get_now():
    return int(time.time())

def validate_user_data(user):
    if not user:
        return "User object is missing"

    for field, expected_type in REQUIRED_FIELDS.items():
        if field not in user:
            return f"Missing field: {field}"
        
        value = user[field]
        
        if value is None:
            return f"Field '{field}' cannot be null"
            
        if not isinstance(value, expected_type):
            return f"Field '{field}' must be of type {expected_type.__name__}"
            
        if expected_type == int and value < 0:
            return f"Field '{field}' must be non-negative"
            
        if expected_type == str and len(value.strip()) == 0:
            return f"Field '{field}' cannot be empty string"
            
    return None

@app.route('/evaluate', methods=['GET'])
def get_evaluate():
    return send_from_directory('static', 'test.html')


@app.route('/evaluate', methods=['POST'])
def evaluate_segments():
    if not request.is_json:
        return jsonify({"error": "Invalid JSON"}), 400
    
    data = request.get_json()
    user_data = data.get("user")
    segments = data.get("segments")

    if not user_data or segments is None:
        return jsonify({"error": "Missing 'user' or 'segments' field"}), 400

    validation_error = validate_user_data(user_data)
    if validation_error:
        return jsonify({"error": validation_error}), 400

    
    conn = sqlite3.connect(':memory:')
    conn.create_function("_now", 0, get_now)
    cursor = conn.cursor()

    try:
        
        cursor.execute("""
            CREATE TABLE users (
                id TEXT, 
                level INTEGER, 
                country TEXT, 
                first_session INTEGER, 
                last_session INTEGER, 
                purchase_amount INTEGER, 
                last_purchase_at INTEGER
            )
        """)

        
        cursor.execute("""
            INSERT INTO users (id, level, country, first_session, last_session, purchase_amount, last_purchase_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user_data['id'],
            user_data['level'],
            user_data['country'],
            user_data['first_session'],
            user_data['last_session'],
            user_data['purchase_amount'],
            user_data['last_purchase_at']
        ))

        results = {}

        
        for segment_name, query in segments.items():
            sql_query = f"SELECT 1 FROM users WHERE {query}"
            
            try:
                cursor.execute(sql_query)
                match = cursor.fetchone()
                results[segment_name] = (match is not None)
            except sqlite3.Error as e:
                conn.close()
                return jsonify({"error": f"Invalid SQL syntax in segment '{segment_name}': {str(e)}"}), 400

        conn.close()
        return jsonify({"results": results}), 200

    except Exception as e:
        conn.close()
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0',port=port, debug=False)