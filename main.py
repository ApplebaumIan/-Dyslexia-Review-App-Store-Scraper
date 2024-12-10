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


def get_app_name_from_api(app_id):
    """
    Fetches the app name using the iTunes Search API.
    """
    url = f"https://itunes.apple.com/lookup?id={app_id}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data["resultCount"] > 0:
            return data["results"][0]["trackName"]  # Extract app name
    return None


def parse_and_filter_reviews(xml_data, app_id):
    root = ET.fromstring(xml_data)
    namespace = {
        'feed': 'http://www.w3.org/2005/Atom',
        'im': 'http://itunes.apple.com/rss'
    }
    entries = root.findall('feed:entry', namespace)

    # Extract the app name from the feed's metadata
    app_name = get_app_name_from_api(app_id)

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
            filtered_reviews.append(
                (app_name, title, author, rating, content, link))

    return filtered_reviews


def contains_dyslexia_keywords(content):
    dyslexia_keywords = ['dyslexia', 'reading difficulty', 'learning disorder', 'reading impairment',
                         'dyslexic', 'As a Dyslexic', 'I am dyslexic', 'neurodivergent', 'difficulty reading', ]
    return any(keyword.lower() in content.lower() for keyword in dyslexia_keywords)


def search_apps_by_keyword(keyword):
    url = f"https://itunes.apple.com/search?term={keyword}&entity=software"
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad status codes
    data = response.json()
    apps = []
    if data["resultCount"] > 0:
        for result in data["results"]:
            apps.append({
                "app_id": result["trackId"],
                "app_name": result["trackName"]
            })
    return apps


def search_all():
    keyword = "dyslexia"
    country = input("Enter the Country Code (e.g., 'us'): ").strip()
    print(f"Searching for apps related to '{keyword}'...")
    apps = search_apps_by_keyword(keyword)
    print(f"Found {len(apps)} apps.")
    setup_database()
    for app in apps:
        app_id = app["app_id"]
        app_name = app["app_name"]
        print(f"Fetching reviews for {app_name} (ID: {app_id})...")
        try:
            xml_data = fetch_reviews(app_id, country)
            filtered_reviews = parse_and_filter_reviews(
                xml_data, app_id)
            for review in filtered_reviews:
                save_review_to_db(*review)
            print(f"Saved {len(filtered_reviews)} reviews for {app_name}.")
        except Exception as e:
            print(f"Failed to fetch reviews for {app_name}: {e}")


def search_appid():
    app_id = input("Enter the App ID: ")
    if 'http' in app_id:
        app_id = app_id.split("/id")[-1].split("?")[0]
    country = input("Enter the Country Code (e.g., 'us'): ").strip()

    print("Fetching reviews...")
    xml_data = fetch_reviews(app_id, country)
    print("Parsing and filtering reviews...")
    filtered_reviews = parse_and_filter_reviews(xml_data, app_id)

    print(f"Found {len(filtered_reviews)} reviews mentioning Dyslexia.")
    for review in filtered_reviews:
        save_review_to_db(*review)

    print("Filtered reviews saved to database.")


def main():
    print("Choose an option:")
    print("1. Search all aps by dyslexia keyword")
    print("2. Search apps with app id")
    choice = input("Enter your choice (1 or 2): ")

    if choice == "1":
        search_all()
    elif choice == "2":
        search_appid()
    else:
        print("Invalid choice! Please select 1 or 2.")


if __name__ == "__main__":
    setup_database()
    main()
