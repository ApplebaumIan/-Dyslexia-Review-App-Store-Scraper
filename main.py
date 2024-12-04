import requests
import xml.etree.ElementTree as ET
import sqlite3

# SQLite database setup
DATABASE_NAME = "app_reviews.db"


def setup_database():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_name TEXT,
            title TEXT,
            author TEXT,
            rating INTEGER,
            content TEXT,
            link TEXT
        )
    ''')
    conn.commit()
    conn.close()


def save_review_to_db(app_name, title, author, rating, content, link):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO reviews (app_name, title, author, rating, content, link)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (app_name, title, author, rating, content, link))
    conn.commit()
    conn.close()


def fetch_reviews(app_id, country):
    url = f"https://itunes.apple.com/{country}/rss/customerreviews/id={app_id}/xml"
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad status codes
    return response.text


def parse_and_filter_reviews(xml_data):
    root = ET.fromstring(xml_data)
    namespace = {
        'feed': 'http://www.w3.org/2005/Atom',
        'im': 'http://itunes.apple.com/rss'
    }
    entries = root.findall('feed:entry', namespace)

    # Extract the app name from the feed's metadata
    app_name = root.find('feed:title', namespace).text if root.find('feed:title', namespace) is not None else "Unknown App"

    filtered_reviews = []
    for entry in entries:
        title = entry.find('feed:title', namespace)
        author = entry.find('feed:author/feed:name', namespace)
        content = entry.find('feed:content', namespace)
        link = entry.find('feed:link', namespace)
        rating = entry.find('im:rating', namespace)

        # Safely extract values or use defaults if not present
        title = title.text if title is not None else "No Title"
        author = author.text if author is not None else "Anonymous"
        content = content.text if content is not None else "No Content"
        link = link.attrib['href'] if link is not None else "No Link"
        rating = int(rating.text) if rating is not None else 0

        if contains_dyslexia_keywords(content):
            filtered_reviews.append((app_name, title, author, rating, content, link))

    return filtered_reviews


def contains_dyslexia_keywords(content):
    dyslexia_keywords = ['dyslexia', 'reading difficulty', 'learning disorder', 'reading impairment']
    return any(keyword.lower() in content.lower() for keyword in dyslexia_keywords)


def main():
    app_id = input("Enter the App ID: ")
    country = input("Enter the Country Code (e.g., 'us'): ").strip()

    print("Fetching reviews...")
    xml_data = fetch_reviews(app_id, country)
    print("Parsing and filtering reviews...")
    filtered_reviews = parse_and_filter_reviews(xml_data)

    print(f"Found {len(filtered_reviews)} reviews mentioning Dyslexia.")
    for review in filtered_reviews:
        save_review_to_db(*review)

    print("Filtered reviews saved to database.")


if __name__ == "__main__":
    setup_database()
    main()
