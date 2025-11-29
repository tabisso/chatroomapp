#Server app for the project 
from flask import Flask , request, jsonify
from werkzeug.exceptions import HTTPException

from db import init_db, create_user, verify_user, add_message, get_messages_after   

app = Flask(__name__)


# ---------- Error handling ----------


@app.errorhandler(Exception)
def handle_errors(error):
    """
    Return nice JSON errors instead of HTML.
    """
    if isinstance(error,HTTPException):
        return jsonify({
            "error" : error.name,
            "message" : error.description
        }), error.code
    

    print("Unexpected error:", repr(error))
    return jsonify({
        "error": "InternalServerError",
        "message": "An unexpected error occurred on the server.",
    }), 500



# ----------  Routes ----------

@app.post("/signup")
def singup():
    """
    Create a new user.
    Expected JSON:
    {
      "username": "...",
      "password": "..."
    }
    """

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error" : "BadRequest", 
                        "message": "Request body must be JSON."}), 400
    
    username = (data.get("username") or  " ").strip()
    password = data.get("password") or ""


    if create_user(username, password):
        return jsonify({"message": "Account created successfully."}), 201
    else:
        return jsonify({"error": "Conflict",
                        "message": "Username already exists."}), 409


@app.post("/login")
def login():
    """
    Log in an existing user.
    Expected JSON:
    {
      "username": "...",
      "password": "..."
    }
    """
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "BadRequest",
                        "message": "Request body must be JSON."}), 400

    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"error": "BadRequest",
                        "message": "Username and password are required."}), 400

    if not verify_user(username, password):
        return jsonify({"error": "Unauthorized",
                        "message": "Invalid username or password."}), 401

    # For now, we don't use tokens; the client remembers the username.
    return jsonify({"message": "Login successful."}), 200


# ---------- Messaging routes ----------

@app.post("/send")
def send_message():
    """
    Send a chat message.
    Expected JSON:
    {
      "username": "...",
      "content": "..."
    }
    """
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "BadRequest",
                        "message": "Request body must be JSON."}), 400

    username = (data.get("username") or "").strip()
    content = (data.get("content") or "").strip()

    if not username or not content:
        return jsonify({"error": "BadRequest",
                        "message": "Username and content are required."}), 400

    message = add_message(username, content)
    return jsonify({"message": "Message sent.", "data": message}), 201


@app.get("/messages")
def messages():
    """
    Get all messages after a given ID.
    Query param: after_id (default 0)
    Example: GET /messages?after_id=5
    """
    after_id_raw = request.args.get("after_id", "0")

    try:
        after_id = int(after_id_raw)
    except ValueError:
        return jsonify({"error": "BadRequest",
                        "message": "after_id must be an integer."}), 400

    msgs = get_messages_after(after_id)
    return jsonify({"messages": msgs}), 200









if __name__ == "__main__":
    # When running directly: make sure DB exists
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)