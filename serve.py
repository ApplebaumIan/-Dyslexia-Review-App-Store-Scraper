from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__, static_folder="dist", static_url_path="")
CORS(app)  # Enable CORS and allow all origins

DATABASE_NAME = "app_reviews.db"

def get_all_reviews():
    """
    Fetches all reviews from the database and formats them as a list of dictionaries.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Query to fetch all reviews
    cursor.execute("SELECT id, app_name, rating, title, content, author FROM reviews")
    rows = cursor.fetchall()
    conn.close()

    # Format the results into the desired JSON structure
    reviews = [
        {
            "id": row[0],
            "app_name": row[1],
            "rating": row[2],
            "title": row[3],
            "content": row[4],
            "author": row[5],
        }
        for row in rows
    ]
    return reviews
# Serve React static files
@app.route("/")
def serve_react():
    return send_from_directory(app.static_folder, "index.html")
@app.route("/reviews", methods=["GET"])
def reviews():
    """
    Endpoint to return all reviews in JSON format.
    """
    reviews = get_all_reviews()
    return jsonify(reviews)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
