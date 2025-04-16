from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from textblob import TextBlob

app = Flask(__name__)
app.secret_key = "your_secret_key"

# User Database
users = {
    "admin": "admin123"
}

# In-Memory Feedback Storage (Replace with a database in production)
feedback_list = []

# YouTube Video Recommendations
VIDEO_RECOMMENDATIONS = {
    "happy": "https://www.youtube.com/watch?v=FQDa6jJpmdA",
    "sad": "https://www.youtube.com/watch?v=zgq4qpVOhAk",
    "angry": "https://www.youtube.com/watch?v=gBfZd9fYEjw",
    "neutral": "https://www.youtube.com/watch?v=C-SPpsk7DAk",
    "excited": "https://www.youtube.com/watch?v=xK8hJNDvuxI",
    "surprised": "https://www.youtube.com/shorts/neyYOeah1jQ",
    "stressed": "https://www.youtube.com/watch?v=xPnvhgVsDlE",
    "lonely": "https://www.youtube.com/watch?v=ZGz35cDXFqo",
    "fear": "https://www.youtube.com/watch?v=C-SPpsk7DAk"
}

@app.route('/')
def home():
    if "user" in session:
        return redirect(url_for("chatbot"))
    return render_template("index.html")

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if username in users:
        return jsonify({"message": "User already exists!"}), 400

    users[username] = password
    session["user"] = username  # Auto-login after registration
    return jsonify({"message": "User registered successfully!", "redirect": url_for("chatbot")}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if users.get(username) == password:
        session["user"] = username
        return jsonify({"message": "User login successful!", "redirect": url_for("chatbot")}), 200
    
    return jsonify({"message": "Invalid credentials!"}), 401

# Admin Login Route
@app.route('/admin', methods=['POST'])
def admin_login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if username == "admin" and password == "admin123":
        session["admin"] = username
        return jsonify({"message": "Admin login successful!", "redirect": url_for("admin_panel")}), 200

    return jsonify({"message": "Invalid admin credentials!"}), 401

# Admin Panel Route
@app.route('/admin_panel')
def admin_panel():
    if "admin" not in session:
        return redirect(url_for("home"))
    return render_template("admin.html")

# Fetch Feedback for Admin Panel
@app.route('/get-feedback', methods=['GET'])
def get_feedback():
    if "admin" not in session:
        return jsonify({"error": "Unauthorized"}), 403
    return jsonify(feedback_list), 200

@app.route('/logout')
def logout():
    session.pop("user", None)
    session.pop("admin", None)
    return redirect(url_for("home"))

@app.route('/chatbot')
def chatbot():
    if "user" not in session:
        return redirect(url_for("home"))
    return render_template("chatbot.html")

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip().lower()

    greetings = {
        "hi": "👋 Hello! How can I assist you today?",
        "hello": "👋 Hello! How can I help you?",
        "hey": "👋 Hey! How’s your day going?"
    }
    farewells = {
        "bye": "👋 Goodbye! Have a great day!",
        "bii": "👋 Goodbye! Have a great day!",
        "goodbye": "👋 Goodbye! Take care!",
        "see you": "👋 See you later!",
        "take care": "😊 Take care! Stay safe!"
    }
    
    if user_message in greetings:
        return jsonify({"reply": greetings[user_message]})
    
    if user_message in farewells:
        return jsonify({"reply": farewells[user_message]})

    keyword_emotions = {
        "happy": "happy",
        "joy": "happy",
        "excited": "excited",
        "sad": "sad",
        "depressed": "sad",
        "angry": "angry",
        "mad": "angry",
        "furious": "angry",
        "calm": "neutral",
        "okay": "neutral",
        "fine": "neutral",
        "good": "neutral",
        "stressed": "stressed",
        "anxious": "stressed",
        "lonely": "lonely",
        "alone": "lonely",
        "shocked": "surprised",
        "surprised": "surprised",
        "fear": "scared",
        "scared": "scared"
    }

    emotion = None
    for word, detected_emotion in keyword_emotions.items():
        if word in user_message:
            emotion = detected_emotion
            break

    if emotion:
        bot_response = f" Feeling {emotion}? Here's something for you: <a href='{VIDEO_RECOMMENDATIONS.get(emotion, 'https://www.youtube.com/')}' target='_blank'>Watch this</a>"
    else:
        bot_response = f"🤔 I may not know your emotion for this, but this might interest you: <a href='{VIDEO_RECOMMENDATIONS['neutral']}' target='_blank'>Watch this</a>"

    return jsonify({"reply": bot_response})

@app.route("/emotion", methods=["POST"])
def emotion_response():
    data = request.json
    emotion = data.get("emotion", "").lower()
    
    response_text = f"I understand you're feeling {emotion}. Here's something to help you!"
    video_link = VIDEO_RECOMMENDATIONS.get(emotion, "https://www.youtube.com/")

    return jsonify({"reply": response_text, "video": video_link})

# Save Feedback
@app.route('/feedback', methods=['POST'])
def feedback():
    data = request.get_json()
    username = session.get("user", "Guest")  # Default to Guest if not logged in
    feedback_message = data.get("message")

    if feedback_message:
        feedback_list.append({"username": username, "message": feedback_message, "date": "2025-03-12"})  # Replace with actual date
        return jsonify({"message": "Thank you for your feedback!"}), 200
    return jsonify({"message": "Feedback cannot be empty!"}), 400

if __name__ == "__main__":
    app.run(debug=True)  